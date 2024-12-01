import base64, secrets, smtplib, re, bcrypt
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
import logging
from pyotp import TOTP
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from foul_lang import profanity_detector, buildTrie

#base
Base = declarative_base()
engine = create_engine('sqlite:///./2fa.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for user
class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True, index=True, unique=True)
    secret_key = Column(String, index=True, nullable=True, unique=True)
    email = Column(String, index=True, unique=True)
    password = Column(String)

# SMTP details latermove to the env file
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'dummy.bloodbank1@gmail.com'
SMTP_PASSWORD = 'awwm kmxo woow hlkh'

Foul_lang_detector = buildTrie()
Base.metadata.create_all(bind=engine)
app = FastAPI()
logger = logging.getLogger(__name__)

#<-----------------functions----------------------->
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#verify email formats (later on depending on the comapny we will change the endpoint)
def is_valid_email(email: str) -> bool:
    # Regular expression for validating an Email with specific domains
    email_regex = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|outlook\.com)$'
    return re.match(email_regex, email) is not None

#<----------------------Two factor auth class--------------------->
class TwoFactorAuth:
    def __init__(self, user_id: str, secret_key: Optional[str], email: str):
        self._user_id = user_id
        self._secret_key = secret_key
        self._email = email
        #OTP lifespan of 90 seconds
        self._totp = TOTP(self._secret_key, interval= 90) if secret_key else None

    @property
    def totp(self) -> Optional[TOTP]:
        return self._totp

    @property
    def secret_key(self) -> Optional[str]:
        return self._secret_key

    @staticmethod
    def _generate_secret_key() -> str:
        secret_bytes = secrets.token_bytes(20)
        secret_key = base64.b32encode(secret_bytes).decode('utf-8')
        return secret_key

    @staticmethod
    def get_or_create_secret_key(db: Session, user_id: str, email: str) -> str:
        db_user = db.query(User).filter(User.user_id == user_id.lower()).first()
        if db_user:
            if db_user.secret_key:
                return db_user.secret_key  # Return existing key
            else:
                secret_key = TwoFactorAuth._generate_secret_key()
                db_user.secret_key = secret_key
                db.commit()
                return secret_key
        secret_key = TwoFactorAuth._generate_secret_key()
        new_user = User(user_id=user_id, secret_key=secret_key, email=email)
        db.add(new_user)
        db.commit()
        return secret_key

    def send_otp_via_email(self, otp_code: str):
        # Create the email content
        message = MIMEMultipart()
        message['From'] = SMTP_USERNAME
        message['To'] = self._email
        message['Subject'] = 'Your OTP Code'

        # Email body
        body = f'Your OTP code is {otp_code}'
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, self._email, message.as_string())

    def verify_totp_code(self, totp_code: str) -> bool:
        if self.totp is None:
            raise ValueError("2FA not enabled")
        return self.totp.verify(totp_code)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


#<---------------Api endpoints-------------------->
@app.post('/add-user/{user_id}')
async def add_user(user_id: str, email: str, password: str, db: Session = Depends(get_db)):
    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Check if the user_id or email already exists
    existing_user_id = db.query(User).filter(User.user_id == user_id.lower()).first()
    existing_email = db.query(User).filter(User.email == email).first()
    
    if existing_user_id:
        raise HTTPException(status_code=400, detail="User ID already exists")
    
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Password strength validation (example regex, adjust as needed)
    if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and contain both letters and numbers")
    
    # Hash the password before storing it
    hashed_password = TwoFactorAuth.hash_password(password)

    # Create a new user
    new_user = User(user_id=user_id, secret_key='', email=email, password=hashed_password)
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    return {"message": "User created successfully", "user_id": user_id, "email": email}


@app.post('/enable-2fa/{user_id}')
async def enable_2fa(user_id: str, email: str, db: Session = Depends(get_db)):
    # Check if the user exists
    db_user = db.query(User).filter(User.user_id == user_id.lower(), User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if 2FA is already enabled
    if db_user.secret_key:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    
    # Generate and set the 2FA secret key
    secret_key = TwoFactorAuth._generate_secret_key()
    db_user.secret_key = secret_key
    db.commit()
    
    return {"message": "2FA enabled", "secret_key": secret_key}



@app.get('/get-user/{email}')
async def get_user(email: str, db: Session = Depends(get_db)):
    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    db_user = db.query(User).filter(User.email == email).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": db_user.user_id, "email": db_user.email}


@app.post('/send-otp/{user_id}')
async def send_otp(user_id: str, email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    #get the user from the db
    db_user = db.query(User).filter(User.user_id == user_id.lower(), User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not db_user.secret_key:
        raise HTTPException(status_code=404, detail="2FA is not enabled.")
    
    two_factor_auth = TwoFactorAuth(user_id, db_user.secret_key, email)
    otp_code = two_factor_auth.totp.now()

    # Send OTP in the background
    background_tasks.add_task(two_factor_auth.send_otp_via_email, otp_code)
    
    logger.info(f"OTP sent to email: {email} for user: {user_id}")

    return {'message': f'OTP sent to your email:{otp_code}'}



@app.post('/verify-totp/{user_id}')
async def verify_totp(user_id: str, totp_code: str, email: str, db: Session = Depends(get_db)):
    # Fetch user from the database
    db_user = db.query(User).filter(User.user_id == user_id.lower(), User.email == email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found. Please verify your id and email.")
    
    if not db_user.secret_key:
        raise HTTPException(status_code=404, detail="2FA is not enabled")
    
    two_factor_auth = TwoFactorAuth(user_id, db_user.secret_key, email)
    is_valid = two_factor_auth.verify_totp_code(totp_code)

    if not is_valid:
        raise HTTPException(status_code=400, detail='Code invalid')
    
    return {'Otp verfied successfully': is_valid}




@app.delete('/delete-user/{user_id}')
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    # Find the user by user_id
    user = db.query(User).filter(User.user_id == user_id.lower()).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Delete the user from the database
        db.delete(user)
        db.commit()
        
        # Log the deletion action
        logger.info(f"User with ID {user_id} deleted successfully")
        
        return {"message": f"User with ID {user_id} deleted successfully"}
    
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")




@app.post('/login')
async def login( password: str, email: Optional[str] = None, user_id: Optional[str] = None,  db: Session = Depends(get_db)):
    # Verify that either email or user_id is provided
    if not email and not user_id:
        raise HTTPException(status_code=400, detail="Either email or user_id must be provided")
    
    # Fetch the user from the database
    db_user = None
    
    if email:
        db_user = db.query(User).filter(User.email == email).first()
    elif user_id:
        db_user = db.query(User).filter(User.user_id == user_id.lower()).first()

    # Check if the user exists
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if not TwoFactorAuth.verify_password(db_user.password, password):
        logger.warning(f"Failed password verification for user: {user_id or email}")

        raise HTTPException(status_code=400, detail="Invalid password")

    logger.info(f"User verified successfully: {user_id or email}")
    return {"message": "User verified successfully"}

    

@app.post('/foul_lang_detector')
async def isFoul(text: str):
    if not isinstance(text, str) or not text.strip():
        logger.warning("Invalid input provided to foul language detector")
        raise HTTPException(status_code=400, detail="Invalid input")
    
    try:
        # Detect foul language
        result = profanity_detector(text, Foul_lang_detector)
        logger.info(f"Foul language detection result: {result}")
        return {"foul_language_detected": result}
    
    except Exception as e:
        logger.error(f"Error during foul language detection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

#add new apis here