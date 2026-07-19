"""
Pydantic schemas - control what the api accepts (requests) and returns (responses).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


def validate_indian_mobile(value: Optional[str]) -> Optional[str]:
    """
    Shared validator: must be exactly 10  digits, numerically greater than
    6666666666 - i.e. must 7, 8, or 9 or be a 66... number above
    6666666666 (in practice this means the first dight must be 6-9, matching
    how Indian mobile numbers are actually allocated by TRAI).
    """
    if value is None:
        return value
    
    if not value.isdigit() or len(value) != 10:
        raise ValueError ("Mobile number must be exactly 10 digits")
    
    if int(value) <= 6666666666:
        raise ValueError("Mobile number must be a valid Indian number greater than 6666666666")
    
    return value

# ----------- Request Schemas ------------

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72, description="8-72 characters")
    phone: Optional[str] = Field(default=None, description="10-digit Indian mobile number")

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        return validate_indian_mobile(v)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = Field(default=None, description="10- digit Indian mobile number")
    profession: Optional[str] = Field(default=None, max_length=100, description="e.g. Salaried, Business Owner, Student, Freelancer")
    monthly_income: Optional[float] = None
    currency: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        return validate_indian_mobile(v)
    
class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72, description="8-72 characters")

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72, description="8-72 characters")

# ------------ Response schemas --------------
class UserResponse(BaseModel):
    user_id : int
    name: str
    email: EmailStr
    phone: Optional[str]=None
    profession: Optional[str]=None
    monthly_income: Optional[float] = None
    currency: str
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RegisterResponse(BaseModel):
    message:str
    email: EmailStr

class MessageResponse(BaseModel):
    message: str

class TokenResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    user : UserResponse

