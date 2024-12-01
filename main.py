from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, MetaData, Table, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
from validations import *
from profantiy_detector import profanity_detector, build_trie, Trie
from fastapi.middleware.cors import CORSMiddleware


from llm_res import setup_model, llm_response

# JWT Secret Key (Store it securely in production)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

DATABASE_URL = "postgresql://omkar:password@localhost/sih_testing"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
users_table = Table("users", metadata, autoload_with=engine)


# Set up a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Reflect tables if needed (optional)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

foul_trie=build_trie()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#<----------------------------APIS--------------------------------------->
@app.post("/signup")
async def add_user(user: UserCreate):
    print(user)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query = insert(users_table).values(
        username=user.username,
        password=hashed_password,
        phone_number=user.phone_number,
        email=user.email
    )
    try:
        with engine.begin() as conn:  # Transaction management
            conn.execute(query)
        return {"message": "User added successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(user: UserLogin):
    with SessionLocal() as session:
        # Compose the query
        stmt = select(users_table).where(users_table.c.username == user.username)

        # Execute the query and fetch the result
        result = session.execute(stmt).fetchone()
    
    # If the result is None, the user wasn't found
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Access the password using the correct index
    stored_password = result[2]  # Assuming password is at index 2, adjust based on your schema

    # Now check against the input password
    if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT token if login is successful
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


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




class TextInput(BaseModel):
    text: str

@app.post('/profanity_detector')
async def text_filter(input: TextInput):
    if not input.text.strip():
        raise HTTPException(status_code=422, detail="Input text is required")

    try:
        # Assuming profanity_detector returns cleaned text.
        user_text = profanity_detector(input.text, foul_trie)
        print(user_text)
        return {"cleaned_text": user_text}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


class Query(BaseModel):
    message: str


llm=setup_model()


@app.post("/chatbot/")
async def get_response(query: Query):
    response = llm_response(query.message, llm)
    return {"response": response}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)