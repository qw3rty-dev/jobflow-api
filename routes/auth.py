from datetime import datetime,UTC

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordRequestForm

from models import User
from database import get_db
from security.jwt_handler import get_current_user,create_access_token,get_current_verified_user
from security.password import verify_password,hash_password,verification_code_generate
from services.email_service import send_verification_mail,send_password_reset_otp,send_welcome_mail
from schemas import UserCreate,UserResponse,TokenResponse,MessageResponse,ChangePassword,VerifyOTP,ForgotPassword,ResetPassword

router= APIRouter(prefix="/auth",tags=["Authentication"])


@router.post("/register",response_model= UserResponse)
def register(user: UserCreate,
             db: Session= Depends(get_db)):
    
    existing_username = db.scalar(select(User).where(User.username == user.username))
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail= "Username already exists")
    
    existing_email = db.scalar(select(User).where(User.email == user.email))
    if existing_email:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT,detail= "Email already exists")
    
    new_user = User(username = user.username,
                    email = user.email,
                    password_hash = hash_password(user.password))
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")

    return new_user


@router.post("/login",response_model= TokenResponse)
def login(formdata: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    
    user = db.scalar(select(User).where(User.email == formdata.username))
    if not user or not verify_password(formdata.password,user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    
    user.last_login = datetime.now(UTC)
    db.commit()
    token = create_access_token(user.id)

    return {
            "access_token": token,
            "token_type": "bearer"
            }


@router.patch("/password_change",response_model=MessageResponse)
def change_password(password: ChangePassword,
                    current_user:User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
     
     if not verify_password(password.current_password,current_user.password_hash):
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail ="Incorrect current password")
     current_user.password_hash = hash_password(password.new_password)
     db.commit()

     return {"message": "Password changed"}


@router.post("/verify_email",response_model=MessageResponse)
def send_verification_code(current_user:User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
         
    if current_user.is_verified:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already verified.")
    verification_code,expires_at = verification_code_generate()
    current_user.verification_code = verification_code
    current_user.verification_expires_at = expires_at
    db.commit()
    send_verification_mail(current_user)

    return {"message":"Verification code sent."}
     

@router.post("/verify_email/confirm",response_model=MessageResponse)
def confirm_verification_code(verify: VerifyOTP ,
                           current_user:User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    
    if current_user.is_verified:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already verified.")
    
    if current_user.verification_expires_at < datetime.now(UTC):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="OTP expired")
    
    if current_user.verification_code != verify.otp:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Incorrect OTP")
    current_user.is_verified = True
    current_user.verification_code = None
    current_user.verification_expires_at = None
    db.commit()
    send_welcome_mail(current_user)

    return {"message":"Verification done."}


@router.post("/forgot_password",response_model=MessageResponse)
def forgot_password(email:ForgotPassword,
                 db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == email.email))
    if not user:
        return {"message":"If an account with that email exists,a password reset email has been sent"}
    
    verification_code,expires_at = verification_code_generate()
    user.verification_code = verification_code
    user.verification_expires_at = expires_at

    db.commit()
    send_password_reset_otp(user)

    return {"message":"If an account with that email exists,a password reset email has been sent"}


@router.post("/reset_password",response_model=MessageResponse)
def reset_password(reset: ResetPassword,
                   db: Session = Depends(get_db)):
    
    user = db.scalar(select(User).where(User.email == reset.email))
    if not user:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid credentials")
    
    if user.verification_expires_at < datetime.now(UTC) :
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="OTP expired")
    
    if user.verification_code != reset.otp:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid credentials")
    
    user.password_hash = hash_password(reset.new_password)
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()

    return {"message":"Password changed"}