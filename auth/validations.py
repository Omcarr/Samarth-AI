from pydantic import BaseModel, EmailStr, field_validator, Field
import regex as re


# Pydantic model for input validation
class UserCreate(BaseModel):
    username: str
    password: str
    phone_number: str
    email: EmailStr
    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        # Regex for validating phone numbers (e.g., +1234567890 or 1234567890)
        phone_pattern = re.compile(r'^\+?\d{10,15}$')  # Allows country code with + and 10-15 digits
        if not phone_pattern.match(value):
            raise ValueError("Invalid phone number format. It should be 10-15 digits, optionally starting with '+'")
        return value


    @field_validator("password")
    def validate_password(cls, value):
        # Password should be at least 8 characters long, contain at least one capital letter and one special character
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r'[\W_]', value):  # Non-word character (special character)
            raise ValueError("Password must contain at least one special character.")
        return value



class UserLogin(BaseModel):
    username: str
    password: str

class TwoFACodeRequest(BaseModel):
    username: str
    code: str

