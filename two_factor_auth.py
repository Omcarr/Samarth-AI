import os, smtplib, jwt, secrets, base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# SMTP details
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# JWT Secret Key
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


#creates a jwt token with validity of 30 mins and encodes it
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_totp_secret():
    # Generate 20 random bytes
    secret_bytes = secrets.token_bytes(20)
    # Encode to Base32
    totp_secret = base64.b32encode(secret_bytes).decode('utf-8')
    return totp_secret