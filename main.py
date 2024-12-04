from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


from sqlalchemy import create_engine, MetaData, Table, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select


from validations import UserCreate, UserLogin, TwoFACodeRequest
from redis import asyncio as aioredis

import bcrypt, jwt, json, base64, secrets,logging, uvicorn, os
from typing import List
from datetime import datetime, timedelta
from pyotp import TOTP

from two_factor_auth import SECRET_KEY, ALGORITHM, oauth2_scheme, send_otp_via_email, create_access_token, generate_totp_secret
from llm_res import setup_model, llm_response
from profantiy_detector import profanity_detector, build_trie, Trie
from ws_setup import WebSocketConnectionManager

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

        # Send the TOTP code via email
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


#works alright, need setup with redis porperly to only get the particular sessions chats
#after the session is closed addthe chats to the history......think about how to scale this
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            new_chat_message = message.get("message")

            # Get LLM response
            response = llm_response(new_chat_message)

            # Save query and response to Redis
            await redis.lpush("chat_history", json.dumps({"message": new_chat_message, "response": response}))

            # Send the response back to the client
            await websocket.send_text(json.dumps({"response": response}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)


#temp api to read all redis storage
@app.get("/chats/")
async def get_chat_history():
    # Retrieve and return the last 20 chat messages from Redis
    chat_history = await redis.lrange("chat_history", 0, 19)
    return [json.loads(chat) for chat in chat_history]


if __name__ == "__main__":
    host_ip=os.getenv("HOST_IP")
    uvicorn.run(app, host=host_ip, port=8000)