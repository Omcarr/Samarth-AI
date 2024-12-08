from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import create_engine, MetaData, Table, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select


from auth.validations import UserCreate, UserLogin, TwoFACodeRequest
from redis import asyncio as aioredis

import bcrypt, jwt, json,logging, uvicorn, os
from datetime import datetime, timedelta
from pyotp import TOTP

from auth.two_factor_auth import SECRET_KEY, ALGORITHM, oauth2_scheme, send_otp_via_email, create_access_token, generate_totp_secret, send_otp_via_sms
from llama3.llm_res import setup_model, llm_response
from profanity.profantiy_detector import profanity_detector, build_trie
from ws.ws_setup import WebSocketConnectionManager


import json
import aiohttp
from voice_chat.whisper import transcribe_audio_whisper
from pydub import AudioSegment
import tempfile


#db connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
#db tables
users_table = Table("users", metadata, autoload_with=engine)


# Connect to Redis
redis = aioredis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

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

#create objects of necessary classes
FOUL_TRIE=build_trie()
LOCAL_LLM=setup_model()
manager = WebSocketConnectionManager()


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
        totp = TOTP(totp_secret, interval=200)
        otp_code = totp.now()  # Generate the current TOTP code

        # Send the TOTP code via email and sms
        #send_otp_via_sms(fetched_user.phone_number, otp_code)
        send_otp_via_email(fetched_user.email, otp_code)
        
        logger.info(f"OTP sent to {fetched_user.email}.")

        #access_token = create_access_token(data={"sub": user.username})

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

        totp_secret = result.totp_secret
        if not totp_secret:
            raise HTTPException(status_code=400, detail="TOTP secret not found.")

        # Create TOTP instance
        totp = TOTP(totp_secret, interval=200)  # Ensure interval is appropriate

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

        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    except HTTPException as http_ex:
        # Log and rethrow HTTP exceptions
        logger.error(f"HTTPException during 2FA verification: {str(http_ex)}")
        raise http_ex
    
    except Exception as e:
        logger.error(f"Error during 2FA verification: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


# <-----------workd--------------------->

#works on postman, have to intergrate with frontend
@app.post("/signup")
async def add_user(user: UserCreate):
    print(user)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    totp_secret = generate_totp_secret()

    query = insert(users_table).values(
        username=user.username,
        password=hashed_password,
        phone_number=user.phone_number,
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


#works on postman, have to intergrate with frontend
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

        return JSONResponse(content={"transcription": transcription_result})
    
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return JSONResponse(status_code=500, content={"message": f"Error processing audio: {e}"})





#works alright, need setup with redis porperly to only get the particular sessions chats
#after the session is closed addthe chats to the history......think about how to scale this
# @app.websocket("/ws/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = json.loads(data)
#             new_chat_message = message.get("message")

#             # Get LLM response
#             response = llm_response(new_chat_message)

#             # Save query and response to Redis
#             await redis.lpush("chat_history", json.dumps({"message": new_chat_message, "response": response}))

#             # Send the response back to the client
#             await websocket.send_text(json.dumps({"response": response}))

#     except WebSocketDisconnect:
#         manager.disconnect(websocket)


# #temp api to read all redis storage
# @app.get("/chats/")
# async def get_chat_history():
#     # Retrieve and return the last 20 chat messages from Redis
#     chat_history = await redis.lrange("chat_history", 0, 19)
#     return [json.loads(chat) for chat in chat_history]


# @app.websocket("/ws/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()

#     try:
#         token = websocket.headers.get("Authorization")
#         if token is None or not token.startswith("Bearer "):
#             raise WebSocketDisconnect(code=1008)

#         token = token.split(" ")[1]
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")
#         if not user_id:
#             raise WebSocketDisconnect(code=1008)

#         redis_key = f"chat_history:{user_id}"

#         while True:
#             data = await websocket.receive_text()
#             message = json.loads(data).get("message")
#             response = llm_response(message)

#             # Save to Redis
#             await redis.lpush(redis_key, json.dumps({"message": message, "response": response}))
#             await redis.expire(redis_key, timedelta(hours=1))

#             await websocket.send_text(json.dumps({"response": response}))

#     except jwt.ExpiredSignatureError:
#         await websocket.close(code=1008, reason="Token expired.")
#     except jwt.DecodeError:
#         await websocket.close(code=1008, reason="Invalid token.")
#     except WebSocketDisconnect:
#         await websocket.close()
#         manager.disconnect(websocket)


# @app.websocket("/ws/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     redis_key = None  # Initialize redis_key with None

#     try:
#         logger.info("WebSocket connection initiated")

#         # Log the received headers
#         #logger.info(f"Received headers: {websocket.headers}")

#         # Extract JWT token from headers
#         token = websocket.headers.get("Authorization")  # Ensure this header is being sent
        
#         if not token or not token.startswith("Bearer "):
#             await websocket.close(code=1008, reason="Missing or invalid token format.")
#             logger.error("Missing or invalid token")
#             return

#         token = token.split(" ")[1]  # Correctly extract the token

#         # Decode the JWT token
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             logger.info(f"Decoded JWT payload: {payload}")
#         except jwt.ExpiredSignatureError:
#             await websocket.close(code=1008, reason="Token expired.")
#             logger.error("Token expired")
#             return
#         except jwt.InvalidTokenError as e:
#             await websocket.close(code=1008, reason="Invalid token.")
#             logger.error(f"JWT error: {str(e)}")
#             return

#         user_id = payload.get("sub")
#         if not user_id:
#             await websocket.close(code=1008, reason="Invalid user id.")
#             logger.error("Invalid user ID in token")
#             return

#         logger.info(f"User {user_id} connected successfully")

#         redis_key = f"chat_history:{user_id}"

#         while True:
#             try:
#                 data = await websocket.receive_text()
#                 logger.debug(f"Received message: {data}")

#                 message = json.loads(data).get("message")

#                 # Simulate response from LLM
#                 response = 'lol'  # Mock response for testing

#                 chat_entry = {
#                     "timestamp": datetime.now().isoformat(),
#                     "message": message,
#                     "response": response
#                 }
#                 await redis.lpush(redis_key, json.dumps(chat_entry))
#                 await redis.expire(redis_key, timedelta(hours=1))

#                 await websocket.send_text(json.dumps({
#                     "response": response,
#                     "timestamp": chat_entry["timestamp"]
#                 }))
#                 logger.debug(f"Response sent: {response}")

#             except Exception as e:
#                 logger.error(f"Error during message processing: {str(e)}")
#                 await websocket.close(code=1011, reason="Error during message processing")
#                 break

#     except WebSocketDisconnect:
#         logger.info("Client disconnected from WebSocket")
#         if redis_key:
#             chat_history = await redis.lrange(redis_key, 0, -1)
#             formatted_history = [json.loads(entry) for entry in chat_history]

#             logger.log(formatted_history)

#             await redis.delete(redis_key)

#         await websocket.close()
#         logger.info("WebSocket closed successfully")


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    redis_key = None

    try:
        logger.info("WebSocket connection initiated")
        logger.info(f"Received headers: {websocket.headers}")

        # Extract JWT token from headers
        token = websocket.headers.get("Authorization")
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
                data = await websocket.receive_text()
                logger.debug(f"Received message: {data}")

                message = json.loads(data).get("message")
                response = 'lol'  # Simulated response for testing

                chat_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user_message": message,
                    "bot_response": response
                }
                await redis.lpush(redis_key, json.dumps(chat_entry))
                await redis.expire(redis_key, timedelta(hours=1))

                await websocket.send_text(json.dumps({
                    "response": response,
                    "timestamp": chat_entry["timestamp"]
                }))
                logger.debug(f"Response sent: {response}")

            except (WebSocketDisconnect, json.JSONDecodeError) as e:
                logger.info("Client disconnected or invalid JSON received")
                break  # Exit the loop if the client disconnects or message is invalid
            except Exception as e:
                logger.error(f"Error during message processing: {str(e)}")
                break  # Exit the loop on unexpected error

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")
        if redis_key:
            chat_history = await redis.lrange(redis_key, 0, -1)

            # Format and log chat history
            formatted_history = []
            for entry in chat_history:
                chat_entry = json.loads(entry)
                formatted_history.append(
                    f"{chat_entry['timestamp']}: User: {chat_entry['user_message']}, Chatbot: {chat_entry['bot_response']}"
                )

            logger.info("Chat History:")
            logger.info("\n".join(formatted_history))
            await redis.delete(redis_key)

        manager.disconnect(websocket)
        logger.info("WebSocket closed successfully")










if __name__ == "__main__":
    host_ip=os.getenv("HOST_IP")
    uvicorn.run(app, host=host_ip, port=8000)