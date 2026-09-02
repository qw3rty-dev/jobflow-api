from datetime import datetime

from pydantic import BaseModel,Field,EmailStr,ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)
    model_config= ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    last_login: datetime| None
    is_verified: bool
    notifications_enabled: bool 
    preferred_locations: list[str]|None
    model_config= ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str
    
class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8,max_length=128)
    model_config= ConfigDict(extra="forbid")


class VerifyOTP(BaseModel):
    otp: str = Field(min_length=6,max_length=6)
    model_config= ConfigDict(extra="forbid")


class ForgotPassword(BaseModel):
    email: EmailStr
    model_config= ConfigDict(extra="forbid")


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6,max_length=6)
    new_password: str = Field(min_length=8,max_length=128)
    model_config= ConfigDict(extra="forbid")

class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8,max_length=128)
    model_config= ConfigDict(extra="forbid")
    

class MessageResponse(BaseModel):
    message: str