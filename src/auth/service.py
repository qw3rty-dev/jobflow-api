from datetime import datetime,UTC,timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status

from src.models import User
from src.security.jwt_handler import create_access_token
from src.security.password import verify_password,hash_password,verification_code_generate
from src.services.email_service import send_verification_mail,send_password_reset_otp,send_welcome_mail


class AuthService:

    def register(self,
                username:str,
                email:str,
                password:str,
                db:Session):
        
        existing_username = db.scalar(select(User).where(User.username == username))
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail= "Username already exists")
        
        existing_email = db.scalar(select(User).where(User.email == email))
        if existing_email:
            raise HTTPException(status_code= status.HTTP_409_CONFLICT,detail= "Email already exists")
        
        new_user = User(username = username,
                        email = email,
                        password_hash = hash_password(password),
                        )
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")

        return new_user


    def login(self,
            email:str,
            password:str,
            db:Session):
        
        user = db.scalar(select(User).where(User.email == email))

        if not user or not verify_password(password,user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
        
        if user.is_deleted:
            if user.deleted_at + timedelta(days=30) <= datetime.now(UTC):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
            
            user.is_deleted = False
            user.deleted_at = None

        user.last_login = datetime.now(UTC)
        db.commit()
        token = create_access_token(user.id)

        return {
                "access_token": token,
                "token_type": "bearer"
                }


    def change_password(self,
                        current_password: str,
                        new_password: str,
                        current_user:User,
                        db:Session):
        
        if not verify_password(current_password,current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail ="Incorrect current password")
        
        current_user.password_hash = hash_password(new_password)
        db.commit()

        return {"message": "Password changed"}


    def send_verification_code(self,
                               current_user:User,
                               db: Session):
            
        if current_user.is_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already verified.")
        
        verification_code,expires_at = verification_code_generate()
        current_user.verification_code = hash_password(verification_code)
        current_user.verification_expires_at = expires_at
        db.commit()
        send_verification_mail(current_user,verification_code)

        return {"message":"Verification code sent."}
        

    def confirm_verification_code(self,
                                  verification_otp:str ,
                                  current_user:User,
                                  db: Session):
        
        if current_user.is_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already verified.")
        
        if current_user.verification_expires_at < datetime.now(UTC) or not verify_password(verification_otp,current_user.verification_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or expired verification code.")
        
        current_user.is_verified = True
        current_user.verification_code = None
        current_user.verification_expires_at = None
        db.commit()
        send_welcome_mail(current_user)

        return {"message":"Verification done."}


    def forgot_password(self,
                        email:str,
                        db: Session):
        
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            return {"message":"If an account with that email exists,a password reset email has been sent"}
        
        verification_code,expires_at = verification_code_generate()
        user.verification_code = hash_password(verification_code)
        user.verification_expires_at = expires_at

        db.commit()
        send_password_reset_otp(user,verification_code)

        return {"message":"If an account with that email exists,a password reset email has been sent"}


    def reset_password(self,
                       email:str,
                       otp:str,
                       new_password:str,
                       db: Session):
        
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid credentials")
        if user.verification_expires_at == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or expired verification code.")
        if user.verification_expires_at < datetime.now(UTC) or not verify_password(otp,user.verification_code) :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or expired verification code.")
            
        user.password_hash = hash_password(new_password)
        user.verification_code = None
        user.verification_expires_at = None
        db.commit()

        return {"message":"Password changed"}

    def delete_account(self,
                       password:str,
                       current_user:User,
                       db: Session ):
        
        if not verify_password(password,current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Incorrect Password")
        
        if not current_user.is_verified:
            db.delete(current_user)
            db.commit()
            return {"message": "account deleted"}
        
        current_user.is_deleted = True         
        current_user.deleted_at = datetime.now(UTC)    
        db.commit()
        return {"message": "Your account has been deactivated and will be permanently deleted after 30 days.You can restore it anytime before then by logging in with your email and password"}     
        
