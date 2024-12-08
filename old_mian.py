from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import create_engine, MetaData, Table, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select


from auth.validations import UserCreate, UserLogin, TwoFACodeRequest
from redis import asyncio as aioredis

import bcrypt, jwt, json, base64, secrets, smtplib,logging,uvicorn
from typing import List
from datetime import datetime, timedelta
from pyotp import TOTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from llama3.llm_res import setup_model, llm_response
from profanity.profantiy_detector import profanity_detector, build_trie, Trie

#db setup
DATABASE_URL = "postgresql://omkar:password@localhost/sih_testing"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
users_table = Table("users", metadata, autoload_with=engine)

# Connect to Redis
redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# Set up a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#fastapi setup
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)  # You can adjust the level as needed
logger = logging.getLogger(__name__)


# JWT Secret Key (Store it securely in production)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# SMTP details latermove to the env file
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'dummy.bloodbank1@gmail.com'
SMTP_PASSWORD = 'awwm kmxo woow hlkh'

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def send_otp_via_email(email:str , otp_code: str):
        # Create the email content
        message = MIMEMultipart()
        message['From'] = SMTP_USERNAME
        message['To'] = email
        message['Subject'] = 'Your OTP Code'

        # Email body
        body = f'Your OTP code is {otp_code}'
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, message.as_string())


foul_trie=build_trie()

def generate_totp_secret():
    # Generate 20 random bytes
    secret_bytes = secrets.token_bytes(20)
    # Encode to Base32
    totp_secret = base64.b32encode(secret_bytes).decode('utf-8')
    return totp_secret

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
            
            # Execute the query and fetch the result
            result = session.execute(stmt).fetchone()
            print(result)
        
        # Check if user exists
        if result is None:
            raise HTTPException(
                status_code=401, 
                detail={
                    "status": "error",
                    "message": "Invalid username or password"
                }
            )
        
        # Verify password
        stored_password = result[1]  # Adjust index based on your table schema
        if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Invalid username or password")
        
        
        totp_secret = result.totp_secret
        if not totp_secret:
            raise HTTPException(status_code=400, detail="TOTP secret not found.")

        logger.info(f"TOTP secret retrieved: '{totp_secret}'")

        # Validate TOTP secret
        if len(totp_secret) % 8 != 0:  # Ensure padding is correct
            raise HTTPException(status_code=400, detail="Invalid TOTP secret padding.")

        # Initialize TOTP
        totp = TOTP(totp_secret, interval=200)
        otp_code = totp.now()  # Generate the current TOTP code

        # Send the TOTP code via email
        send_otp_via_email(result.email, otp_code)
        logger.info(f"OTP sent to {result.email}.")

        access_token = create_access_token(data={"sub": user.username})

        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username
        }

    except Exception as e:
        logger.error(f"An error occurred during login: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


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

# <-----------workd--------------------->














@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if not token:  # Check if there is a token
        raise HTTPException(status_code=403, detail="Missing token")
    
    try:
        # Attempt to decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # If successful, you can add additional logic here if necessary, like logging or invalidation logic
        return {"message": "Logged out successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.delete("/delete_user/{username}")
async def delete_user(username: str):
    query = delete(users_table).where(users_table.c.username == username)
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# class TextInput(BaseModel):
#     text: str

@app.post('/profanity_detector')
async def text_filter(input: str):
    if not input.text.strip():
        raise HTTPException(status_code=422, detail="Input text is required")

    try:
        # Assuming profanity_detector returns cleaned text.
        user_text = profanity_detector(input.text, foul_trie)
        print(user_text)
        return {"cleaned_text": user_text}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


# class Query(BaseModel):
#     message: str


llm=setup_model()

# A connection manager to handle active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            query = message.get("query")

            # Get LLM response
            response = llm_response(query)

            # Save query and response to Redis
            await redis.lpush("chat_history", json.dumps({"query": query, "response": response}))

            # Send the response back to the client
            await websocket.send_text(json.dumps({"response": response}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/chats/")
async def get_chat_history():
    # Retrieve and return the last 20 chat messages from Redis
    chat_history = await redis.lrange("chat_history", 0, 19)
    return [json.loads(chat) for chat in chat_history]




# @app.post("/chatbot/")
# async def get_response(query: Query):
#     response = llm_response(query.message, llm)
#     return {"response": response}


# @app.post('/ws'):




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)