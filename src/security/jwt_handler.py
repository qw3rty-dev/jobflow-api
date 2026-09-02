import os
from datetime import datetime,UTC,timedelta
from dotenv import load_dotenv

import jwt
from fastapi import status
from fastapi import HTTPException,Depends,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from src.database import get_db
from src.models import User

load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM= "HS256"

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(user_id:int)->str:

    expire= datetime.now(UTC)+ timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM        
    )

def verify_access_token(token:str)-> int:

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            [ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= "Invalid access token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= "Unauthorized")
    user_id = int(sub)
    return user_id

def create_refresh_token(user_id:int)->str:

    expire= datetime.now(UTC)+ timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM        
    )

def verify_refresh_token(token:str)-> int:

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            [ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= "Invalid refresh token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail= "Unauthorized")
    user_id = int(sub)
    return user_id


def get_current_user(token: str = Depends(oauth2_scheme),
                        db:Session = Depends(get_db)):
    
    current_user_id = verify_access_token(token)
    current_user = db.scalar(select(User).where(User.id == current_user_id))
    if not current_user:
       raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication credentials")
    return current_user


def get_current_verified_user(current_user: User= Depends(get_current_user)):
    
    if not current_user.is_verified:
       raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,detail="Please verify your email to use this feature.")
    return current_user

def get_current_admin(current_user: User= Depends(get_current_user)):
    
    if not current_user.is_admin:
       raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,detail="Admin privileges required.")
    return current_user


