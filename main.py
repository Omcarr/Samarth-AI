from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, MetaData, Table, insert, delete, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
import sqlalchemy as sa
from auth.validations import UserCreate, UserLogin, TwoFACodeRequest
from redis import asyncio as aioredis
import bcrypt, jwt, json,logging, uvicorn, os, uuid
from datetime import datetime, timedelta
from pyotp import TOTP
from auth.two_factor_auth import SECRET_KEY, ALGORITHM, oauth2_scheme, send_otp_via_email, create_access_token, generate_totp_secret, send_otp_via_sms
from Rag.llm_res import setup_model, llm_response
from profanity.profantiy_detector import profanity_detector, build_trie
from ws.ws_setup import WebSocketConnectionManager
from db_files.chat_history import generate_chat_summary
import json
from voice_chat.whisper import transcribe_audio_whisper
from pydub import AudioSegment
import tempfile
import asyncio
from sqlalchemy.dialects.postgresql import JSONB
import functools
from redis import Redis
from sqlalchemy.exc import SQLAlchemyError
from pdf2image import convert_from_bytes
from groq import Groq
from PIL import Image

# from langchain.chains import ConversationChain, LLMChain
# from langchain_core.prompts import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )


#db connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine=create_engine(DATABASE_URL, future=True) 
metadata = MetaData()
Base = declarative_base()

SYSTEM_DICT_FILE="system_dict.txt"

#db tables
users_table = Table("users", metadata, autoload_with=engine)
chat_history_table=Table("chat_history", metadata, autoload_with=engine)

# Connect to Redis
redis = aioredis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

redis_sync_client = Redis(host='localhost', port=6379, db=0)


# Set up a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#fastapi setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create objects of necessary classes
FOUL_TRIE = build_trie()
LOCAL_LLM = setup_model()
manager = WebSocketConnectionManager()
OTP_LIFESPAN= 300 #seconds
MAX_PINNED_CHATS=3



#chat history storage
class ChatHistory(Base):
    __tablename__ = 'chat_history'

    # Use UUID as the primary key to ensure global uniqueness
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Explicitly generate a separate session_id using UUID
    session_id = sa.Column(sa.String(36), nullable=False, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    user_id = sa.Column(sa.String, nullable=False)
    bot_mode = sa.Column(sa.String, nullable=True, default='default')
    chat_summary = sa.Column(sa.Text, nullable=True)
    full_chat_history = sa.Column(JSONB, nullable=False)
    total_messages = sa.Column(sa.Integer, nullable=False)
    start_time = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.now())
    end_time = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.now())
    
    def __repr__(self):
        return f"<ChatHistory(session_id={self.session_id}, user_id={self.user_id})>"
   
def save_chat_history(redis_client, redis_key, SessionLocal, user_id, logger):
    """
    Save chat history to PostgreSQL in a synchronous manner.
    Args:
        redis_client: Synchronous Redis client.
        redis_key: Redis key for chat history.
        SessionLocal: SQLAlchemy Session Factory.
        user_id: User identifier.
        logger: Logging object.
    """
    try:
        # Retrieve chat history synchronously
        chat_history = redis_client.lrange(redis_key, 0, -1)

        if not chat_history:
            logger.warning(f"No chat history found for key: {redis_key}")
            return

        # Parse chat history
        parsed_history = [json.loads(entry.decode('utf-8')) for entry in chat_history]

        # Generate chat summary
        chat_summary = generate_chat_summary(parsed_history)

        # Extract session details
        first_entry = parsed_history[0]
        last_entry = parsed_history[-1]

        start_time = datetime.fromisoformat(first_entry['timestamp'])
        end_time = datetime.fromisoformat(last_entry['timestamp'])
        session_id = first_entry.get('session_id', str(uuid.uuid4()))

        # Save to the database synchronously
        db_session = SessionLocal()
        try:
            new_chat_record = ChatHistory(
                user_id=user_id,
                session_id=session_id,
                bot_mode=first_entry.get('bot_mode', 'default'),
                chat_summary=chat_summary,
                full_chat_history=parsed_history,
                total_messages=len(parsed_history),
                start_time=start_time,
                end_time=end_time
            )

            db_session.add(new_chat_record)
            db_session.commit()
            logger.info(f"Chat history saved for user {user_id}, session {session_id}")
        except Exception as commit_error:
            db_session.rollback()
            logger.error(f"Error committing chat history: {str(commit_error)}")
            raise
        finally:
            db_session.close()

    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")





#<----------------------------APIS--------------------------------------->
# Login Endpoint
@app.post("/login")
async def login(user: UserLogin):
    try:
        # Create a database session
        with SessionLocal() as session:
            # Compose the query to find the user
            stmt = select(users_table).where(
                users_table.c.username == user.username
            )
            
            fetched_user = session.execute(stmt).fetchone() #returns the users row as a tuple
            
        # Check if user exists
        if fetched_user is None:
            raise HTTPException(status_code=401, detail={"message": "Invalid username or password"})
        logger.info(fetched_user)
        
        
        stored_password = fetched_user.password.encode('utf-8') #getting pasword from db into the utf-8 format
        totp_secret = fetched_user.totp_secret


        #compare the passwords
        if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password):
            raise HTTPException(status_code=400, detail="Invalid username or password")
        
        #while signing up totp_secrte was not generated------>this wont happen since admin will be the one creating the user logins
        if not totp_secret:
            raise HTTPException(status_code=400, detail="TOTP secret not found.")

        # Initialize TOTP
        totp = TOTP(totp_secret, interval=OTP_LIFESPAN)
        otp_code = totp.now()  # Generate the current TOTP code
        logger.info(otp_code)

        # Send the TOTP code via email and sms
        #send_otp_via_sms(fetched_user.phone_number, otp_code)
        send_otp_via_email(fetched_user.email, otp_code)
        
        return {
            "status": "success",
            "message": "OTP sent, please verify 2FA.",
            "username": user.username
        }

    except Exception as e:
        logger.error(f"An error occurred during login: {str(e)}")
        raise HTTPException(status_code=401, detail={"message": str(e)})


@app.post("/verify-2fa")
async def verify_2fa(request: TwoFACodeRequest):
    username = request.username
    code = request.code
    try:
        with SessionLocal() as session:
            # Fetch user details including TOTP secret
            stmt = select(users_table).where(users_table.c.username == username)
            result = session.execute(stmt).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        isAdmin=result.is_admin
        logger.info(isAdmin)
        totp_secret = result.totp_secret
        if not totp_secret:
            raise HTTPException(status_code=400, detail="TOTP secret not found.")

        # Create TOTP instance
        totp = TOTP(totp_secret, interval=OTP_LIFESPAN)  # Ensure interval is appropriate

        # Log the expected OTP for debugging
        expected_code = totp.now()
        logger.info(f"Expected OTP code: {expected_code}")
        logger.info(f"User provided OTP code for verification: {code}")

        # Verify the provided OTP
        if not totp.verify(code):
            logger.warning("Invalid 2FA code provided.")
            raise HTTPException(status_code=401, detail="Invalid 2FA code.")

        # Regenerate access token on successful 2FA verification
        access_token = create_access_token(data={"sub": username})

        # #get chat historys
        # Pinned_chats=fetch_pinned_chats(username)
        # prev_chats=fetch_previous_chats(username)

        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "username": username,
            "isAdmin": isAdmin,
            # "Pinned_chats":Pinned_chats,
            # "Previous_chats": prev_chats, 
        }
    
    
    except HTTPException as http_ex:
        # Log and rethrow HTTP exceptions
        logger.error(f"HTTPException during 2FA verification: {str(http_ex)}")
        raise http_ex
    
    except Exception as e:
        logger.error(f"Error during 2FA verification: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


#works on postman, have to intergrate with frontend
@app.post("/signup")
async def add_user(user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    totp_secret = generate_totp_secret()

    phone=user.phone_number
    if phone[0]!='+':
        phone='+91'+phone

    query = insert(users_table).values(
        username=user.username,
        password=hashed_password,
        phone_number=phone,
        email=user.email,
        totp_secret=totp_secret,
    )

    try:
        with engine.begin() as conn:  # Transaction management
            conn.execute(query)
        return {"message": "User added successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#works on postman, have to intergrate with frontend
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if not token:  # Check if there is a token
        raise HTTPException(status_code=403, detail="Missing token")
    
    try:
        # Attempt to decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        logger.info("logged out succesfully")
        return {"message": "Logged out successfully"}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.DecodeError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

#works on postman, have to intergrate with frontend
@app.delete("/delete_user/{username}")
async def delete_user(username: str):
    query = delete(users_table).where(users_table.c.username == username)
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


#session wise redis- chat history storage. wehn a session is cleared it stores it into the postgres
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    redis_key = None
    user_id = None
    session_id = str(uuid.uuid4())

    try:
        logger.info("WebSocket connection initiated")
        logger.info(f"Received headers: {websocket.headers}")
        logger.info(websocket.query_params.get("bot_mode", "1234"))
        
        # Extract JWT token from headers
       # token = websocket.headers.get("Authorization")
        #logger.info(token)

        token = websocket.query_params.get("Authorization")
        
        logger.info(token)
        if token:
            if not token.startswith("Bearer "):
                await websocket.close(code=1008, reason="Missing or invalid token format.")
                logger.error("Missing or invalid token format")
                return
            token = token.split(" ")[1]
        else:
            await websocket.close(code=1008, reason="Missing Authorization header.")
            logger.error("Missing Authorization header")
            return

        # Decode JWT token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=1008, reason="Invalid user ID.")
                logger.error("Invalid user ID in token")
                return

            logger.info(f"User {user_id} connected successfully")
            redis_key = f"chat_history:{user_id}"
            bot_mode= websocket.query_params.get("bot_mode","rag")

            users_chat_history = FetchChatHistory(user_id)
            
            # Send chat history to the frontend
            await websocket.send_json({
                "type": "chat_history",
                "session_id": session_id,
                "chat_history": users_chat_history
            })



            # logger.info(redis_key)
            # logger.info(bot_mode)


        except jwt.ExpiredSignatureError:
            await websocket.close(code=1008, reason="Token expired.")
            logger.error("Token expired")
            return
        except jwt.InvalidTokenError as e:
            await websocket.close(code=1008, reason="Invalid token.")
            logger.error(f"JWT error: {str(e)}")
            return

        while True:
            try:
                # Wait for a single message
                data = await websocket.receive_text()
                message_data = json.loads(data)
               # logger.info(message_data)
                
                # Extract message and bot mode
                message = message_data.get("message")
                bot_mode = message_data.get("bot_mode", "default")
                
                #session memoruy=---->?
                # Get response from LLM    
                #current session memory ro session memeory for llm
                chat_history = await redis.lrange(redis_key, 0, -1)
                # print(chat_history)
                session_memory = []
                for entry in chat_history:
                    chat_entry = json.loads(entry)
                    user_message = chat_entry.get("user_message", "N/A")  # Default to "N/A" for null
                    bot_response = chat_entry.get("bot_response", "N/A")  # Default to "N/A" for null
                    # timestamp = chat_entry.get("timestamp", "N/A")  # Default to "N/A" for missing timestamp
                    
                    session_memory.append(
                        {'user': {user_message}, 'chat': {bot_response}}
                    )
                response =  llm_response(message)
                
                # Prepare chat entry
                chat_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user_message": message,
                    "bot_response": response,
                    "user_id": user_id,
                    "bot_mode": bot_mode,
                    "session_id": session_id
                }
                
                # Store in Redis
                await redis.lpush(redis_key, json.dumps(chat_entry))
                await redis.expire(redis_key, timedelta(hours=1))
                
                # Send response back
                await websocket.send_text(json.dumps({
                    "response": response,
                    # "timestamp": chat_entry["timestamp"],
                    # "bot_mode": bot_mode
                }))
                
                #logger.debug(f"Response sent: {response}")
            

            except WebSocketDisconnect:
                logger.info("Client disconnected from WebSocket")
                break  # Exit the while loop on disconnect
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                break  # Exit the loop on invalid JSON
            except Exception as e:
                logger.error(f"Error during message processing: {str(e)}")
                break  # Exit the loop on unexpected error

    finally:
        if redis_key:
            # Retrieve chat history synchronously
            chat_history = await redis.lrange(redis_key, 0, -1)

            # Log chat history
            logger.info(json.dumps(chat_history, indent=4))

            # Use partial to pass parameters to the synchronous function
            save_func = functools.partial(
                save_chat_history,
                redis_sync_client,  # Ensure this is a synchronous Redis client
                redis_key,
                SessionLocal,
                user_id,
                logger
            )

            # Run synchronous function in a thread pool
            await asyncio.get_event_loop().run_in_executor(None, save_func)

            # Cleanup Redis
            await redis.delete(redis_key)

        manager.disconnect(websocket)
        logger.info("WebSocket closed successfully")


def FetchChatHistory(user):
    Pinned_chats=fetch_pinned_chats(user)
    prev_chats=fetch_previous_chats(user)

    return {
        "Pinned_chats":Pinned_chats,
        "Previous_chats": prev_chats, 
    }

#needs better system maintained dict, need a better solution instead of this api call
@app.post('/profanity_detector')
async def text_filter(input: str):
    if not input.text.strip():
        raise HTTPException(status_code=422, detail="Input text is required")

    try:
        # Assuming profanity_detector returns cleaned text.
        user_text = profanity_detector(input.text, FOUL_TRIE)
        print(user_text)
        return {"cleaned_text": user_text}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


#to get users audio and get it transcribed from whisper model
@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    logger.info('Received audio file for transcription.')

    try:
        # Save the uploaded audio to a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, audio.filename)

        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Convert audio file to WAV format (using Pydub)
        audio_wav_path = os.path.join(temp_dir, "converted_audio.wav")
        
        # Load the uploaded file into Pydub
        audio_segment = AudioSegment.from_file(temp_audio_path)
        
        # Export it as WAV format
        audio_segment.export(audio_wav_path, format="wav")
        
        # Log the conversion
        logger.info(f"Converted audio file saved as WAV: {audio_wav_path}")

        # Now send the WAV file to the Whisper transcription function
        transcription_result = transcribe_audio_whisper(audio_wav_path)

        # Clean up the temporary files after processing
        os.remove(temp_audio_path)
        os.remove(audio_wav_path)

        logger.info(transcription_result)
        print(transcription_result)

        return JSONResponse(content={"transcription": transcription_result})
    
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return JSONResponse(status_code=500, content={"message": f"Error processing audio: {e}"})


#api for resending the otp---> send username based on it send the otp again
@app.post('/resend_otp')
async def resend_otp(user_trying_to_login):
    try:
        with SessionLocal() as session:
                # Compose the query to find the user
                #logger.info(request,user_trying_to_login)
                stmt = select(users_table).where(
                    users_table.c.username == user_trying_to_login
                )
                
                fetched_user = session.execute(stmt).fetchone() #returns the users row as a tuple
            
        # Check if user exists
        if fetched_user is None:
            raise HTTPException(status_code=401, detail={"message": "Invalid username or password"})
        logger.info(fetched_user)
        
        totp_secret = fetched_user.totp_secret
        # Initialize TOTP
        totp = TOTP(totp_secret, interval=OTP_LIFESPAN)
        otp_code = totp.now()  # Generate the current TOTP code

        # Send the TOTP code via email and sms
        #send_otp_via_sms(fetched_user.phone_number, otp_code)
        send_otp_via_email(fetched_user.email, otp_code)
        
        return {
            "status": "success",
            "message": "OTP sent again, please verify 2FA.",
            "username": user_trying_to_login
        }

    except Exception as e:
        logger.error(f"An error occurred during login: {str(e)}")
        raise HTTPException(status_code=401, detail={"message": str(e)})



@app.get("/chat-history")
def get_chat_history(chat_session_id: str):
    """
    Retrieve full chat history for a specific session.
    """
    try:
        with SessionLocal() as session:
            # Fetch user details including TOTP secret
            stmt = select(chat_history_table).where(chat_history_table.c.session_id == chat_session_id)
            chat_record = session.execute(stmt).fetchone()

        if not chat_record:
            raise HTTPException(status_code=404, detail="Chat history not found")
        
        # Construct and return the response
        return {
            "session_id": chat_record.session_id,
            "summary": chat_record.chat_summary,
            "total_messages": chat_record.total_messages,
            "bot_mode": chat_record.bot_mode,
            "start_time": chat_record.start_time,
            "end_time": chat_record.end_time,
            "full_history": chat_record.full_chat_history,
            "is_pinned": chat_record.is_pinned,
        }

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


#operations realted to pinning or unpinng 
@app.get("/toggle_isPinned")
async def toggle_isPinned(chat_session_id:str):
    try:
        with SessionLocal() as session:
            # Fetch user details including TOTP secret
            stmt = select(chat_history_table).where(chat_history_table.c.session_id == chat_session_id)
            chat_record = session.execute(stmt).fetchone()

        if not chat_record:
            raise HTTPException(status_code=404, detail="Chat history not found")
        
        count_stmt = select(func.count()).where(chat_history_table.c.is_pinned == True)
        total_pinned_count = session.execute(count_stmt).scalar()

        pin_status=chat_record.is_pinned

        if pin_status==False and total_pinned_count==MAX_PINNED_CHATS:
            return {
                    "message": f"You have {MAX_PINNED_CHATS} pinned chats."
                }
        elif pin_status==False:
                # If it's not pinned, pin it
                update_stmt = update(chat_history_table).where(chat_history_table.c.session_id == chat_session_id).values(is_pinned=True)
                session.execute(update_stmt)
                session.commit()
                return {"message": "Chat has been pinned successfully."}
        else:
                # If it's already pinned, unpin it
                update_stmt = update(chat_history_table).where(chat_history_table.c.session_id == chat_session_id).values(is_pinned=False)
                session.execute(update_stmt)
                session.commit()
                return {"message": "Chat has been unpinned successfully."}

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

#delete the chat session
@app.get("/delete_chat_session")
async def delete_chat_session(chat_session_id: str):
    try:
        with SessionLocal() as session:
            # Fetch the chat history by session_id
            stmt = select(chat_history_table).where(chat_history_table.c.session_id == chat_session_id)
            chat_record = session.execute(stmt).fetchone()

            if not chat_record:
                raise HTTPException(status_code=404, detail="Chat history not found")
            
            # Delete the chat history record from the table
            delete_stmt = delete(chat_history_table).where(chat_history_table.c.session_id == chat_session_id)
            session.execute(delete_stmt)
            session.commit()

            return {"message": "Chat session deleted successfully."}
    
    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

#fetches last 5 chats that are not pinned
def fetch_previous_chats(username: str):
    try:
        with SessionLocal() as session:
            # Select chats where username matches and chats are not pinned, then order by timestamp
            stmt = select(chat_history_table).where(
                (chat_history_table.c.user_id == username) &
                (chat_history_table.c.is_pinned == False)  # Assuming pinned is a boolean column
            ).order_by(chat_history_table.c.end_time.desc()).limit(5)
            
            chat_session = session.execute(stmt).fetchall()
        if not chat_session: return {}

        chat_id_and_title=[]
        for chat in chat_session:
            session_id=chat[1]
            session_title=chat[4]

            chat_id_and_title.append({'session_id':session_id,'session_title':session_title})

        return chat_id_and_title

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



#returns all the pinned chats
def fetch_pinned_chats(username):
    try:
        with SessionLocal() as session:
            stmt = select(chat_history_table).where(
                (chat_history_table.c.user_id == username) &
                (chat_history_table.c.is_pinned == True)
            )
            pinned_chats = session.execute(stmt).fetchall()
        
        if not pinned_chats: return {}

        chat_id_and_title=[]
        for chat in pinned_chats:
            session_id=chat[1]
            session_title=chat[4]

            chat_id_and_title.append({'session_id':session_id,'session_title':session_title})

        return chat_id_and_title

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific exceptions
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle generic exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



from pathlib import Path
import shutil
from datetime import datetime
from typing import List
import base64
import pdfplumber
import io
import Rag.model as model

UPLOAD_DIR = Path("files")
UPLOAD_DIR.mkdir(exist_ok=True)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
groq_api = os.environ["GROQ_API_KEY"]

async def stream_generate_async(messages):
    client = Groq(api_key = groq_api)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.4,
        max_tokens=1024,
        top_p=0.9,
        stream=True,
        stop=None,
    )
    for chunk in completion:
        yield chunk.choices[0].delta.content or ""
        await asyncio.sleep(0)

def generate_async(messages):
    client = Groq(api_key = groq_api)
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=messages,
        temperature=0.4,
        max_tokens=1024,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    print("test99")
    return completion.choices[0].message.content

def formatter(msg):
    prompt = """Format the following text to make it more readable:

        {unformatted_text}

        Please apply the following formatting:
        - Use **bold** for key terms
        - Use *italic* for important concepts
        - Add bullet points where appropriate
        - Improve overall structure and readability
        - Make the text more engaging
    """


    prompt = prompt.format(unformatted_text= msg)
    messages=[
        {
            "role": "system",
            "content": """
                You are a helpful chatbot that formats the text given by the user in markdown format.
            """
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    client = Groq(api_key = groq_api)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.4,
        max_tokens=4096,
        top_p=0.9,
        stream=True,
        stop=None,
    )

    return completion.choices[0].message.content
    

query_format = """
Question: 
{question}\n\n

Context:
{context}
"""


@app.websocket("/askpdf")
async def websocket_askpdf(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            query = await websocket.receive_text()
            question = json.loads(query)
            print(str(query))
            query = question.get("message")
            print(query)

           #query_in_time=datetime.now()
            file_data = question.get("file")
            if file_data:
                file_content = base64.b64decode(file_data["content"])
                file_name = file_data["name"]
                file_type = file_data["type"]
                if file_type == 'application/pdf':
                    pdf_file = io.BytesIO(file_content)
                    image=Image.open(pdf_file)
                    # text = pytesseract.image_to_string(image)
                    text =""
                    with pdfplumber.open(pdf_file) as pdf:
                        for page in pdf.pages:
                            text += page.extract_text() or ""  # handle empty pages
                        print("PDF content:", text)
                # files_folder = 'files'
                # os.makedirs(files_folder, exist_ok=True)  # Create folder if it doesn't exist

                # if file_type == 'application/pdf':
                #     # Save the PDF to the 'files' folder
                #     pdf_path = os.path.join(files_folder, file_name)
                #     with open(pdf_path, 'wb') as f:
                #         f.write(file_content)

                #     # Convert PDF to images
                #     images = convert_from_bytes(file_content)
                #     text = ''

                #     # Extract text from each image using Tesseract
                #     for image in images:
                #         text += pytesseract.image_to_string(image)

                    print("Extracted text from PDF:", text)


                prompt = query_format.format(question=query, context=text)
                messages=[
                    {
                        "role": "user",
                        "content": """
                            You are a context-based Q&A assistant. Your role is to:
                            1. Answer questions using ONLY the provided context, never external knowledge
                            2. Keep answers concise unless specifically asked to elaborate and also properly format and beautify it.
                            3. If asked to summarize the document(pdf, word, etc) you summarize it instead of doing a Q&A
                            4. If the context doesn't contain enough information to answer fully:
                            - State this clearly
                            - Don't speculate or make assumptions
                            - Indicate what information is missing
                            Remember: Accuracy and proper source attribution are your top priorities.
                        """
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
                async for chunk in stream_generate_async(messages):
                    await websocket.send_text(chunk)

                continue

            print("test")
            file_names = os.listdir('./summaries/')
            print("test 3")
            print(file_names)
            files_paths = '\n'.join(file_names)
            print("test 4")
            print(files_paths)

            # if "bullet" in query:
            #     with open("summaries/Data_Loss_Prevention_Policy_badWords.txt", 'r') as file:
            #         content = file.read()
            #         await websocket.send_text(content)

            if "summary" in query.lower() or "summarize" in query.lower() or "summarise" in query.lower():
                sysprompt = '''You are an intelligent query routing system that determines the correct file path for the given query.
                    Here are the file paths of the pdfs:
                    {file_paths}\n
                    The output should be just one word: the appropriate file_path.
                    '''
                print("test 6")
                sysprompt = sysprompt.format(file_paths=files_paths)
                print("test 5")
                messages=[
                    {
                        "role": "system",
                        "content": sysprompt
                    },
                    {
                        "role": "user",
                        "content": query,
                    }
                ]
                print("test2")
                mode = generate_async(messages).strip()
                print(mode)
                
                if mode.endswith(".txt"):
                    mode = mode[:-4]
                
                with open(f'./summaries/{mode}.txt', 'r') as file:
                    content = file.read()
                    await websocket.send_text(content)
                
            else:
                # ansformat= await model.llm_response(query=query)
                await websocket.send_text(await model.llm_response(query=query))
            
            # async for chunk in formatter(ansformat):
            #     await websocket.send_text(chunk)
        

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        #save the chat history
        await websocket.close()



@app.post("/pdfupload")
async def upload_documents(documents: List[UploadFile] = File(...)):
    saved_files = []

    for upload_file in documents:
        file_path = UPLOAD_DIR / upload_file.filename
        
        # Save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        saved_files.append({
            "original_name": upload_file.filename,
            "saved_path": str(file_path)
        })

        await model.add_document(file_path=f'{UPLOAD_DIR}/{upload_file.filename}', file_name=upload_file.filename)


    return {
        "message": "Upload successful",
        "files": saved_files
    }


@app.post('/system_dict')
def AddWordToSystemDict(word):
    #add to system dict txt file
    if not word:
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    print(word)
    print(SYSTEM_DICT_FILE)
    # Ensure the dictionary file exists
    if not os.path.exists(SYSTEM_DICT_FILE):
        with open(SYSTEM_DICT_FILE, "w") as file:
            pass  # Create the file if it doesn't exist

    # Check if the word already exists in the dictionary
    with open(SYSTEM_DICT_FILE, "r") as file:
        if word in (line.strip() for line in file):
            return {'message':f'{word} already exists'}

    # Append the word to the dictionary
    with open(SYSTEM_DICT_FILE, "a") as file:
        file.write(f"{word}\n")

    return {"message": f"Word '{word}' added to system dictionary successfully"}



if __name__ == "__main__":
    host_ip=os.getenv("HOST_IP")
    uvicorn.run(app, host=host_ip, port=8080)