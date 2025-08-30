import os, smtplib, jwt, secrets, base64
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from twilio.rest import Client

# SMTP details
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# JWT Secret Key
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#twiilio details
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER =  os.getenv("TWILIO_PHONE_NUMBER")

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

def send_otp_via_sms(phone_number:str, otp:str):

    # Message content
    message_body = f"Your OTP is: {otp}. Please use this to verify your identity for logging into the chatbot"

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"Message SID: {message.sid}")
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

#creates a jwt token with validity of 30 mins and encodes it

# def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
#     to_encode = data.copy()
    
#     # Always use UTC for JWT
#     expire = datetime.now(timezone.utc) + expires_delta
#     to_encode.update({"exp": int(expire.timestamp())})
#     encoded_jwt = jwt.encode(to_encode, "your-secret-key", algorithm="HS256")
    
#     return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})

    print(f"Encoding JWT with payload: {to_encode}, SECRET_KEY type={type(SECRET_KEY)}")
    encoded_jwt = jwt.encode(to_encode, "your-secret-key", algorithm="HS256")
    return encoded_jwt



def generate_totp_secret():
    # Generate 20 random bytes
    secret_bytes = secrets.token_bytes(20)
    # Encode to Base32
    totp_secret = base64.b32encode(secret_bytes).decode('utf-8')
    return totp_secret

# send_otp_via_sms(
# phone_number='+917304767827',
# otp='674537'
# )