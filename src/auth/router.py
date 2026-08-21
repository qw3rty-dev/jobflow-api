from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,status
from fastapi.security import OAuth2PasswordRequestForm

from src.models import User
from src.database import get_db
from src.security.jwt_handler import get_current_user,get_current_verified_user
from .schemas import UserCreate,UserResponse,TokenResponse,MessageResponse,ChangePassword,VerifyOTP,ForgotPassword,ResetPassword,DeleteAccountRequest



from .service import AuthService

router= APIRouter(prefix="/auth",tags=["Authentication"])
auth_service = AuthService()

@router.post("/register",response_model= UserResponse,status_code=status.HTTP_201_CREATED)
def register(user: UserCreate,
             db: Session= Depends(get_db)):
    
    new_user = auth_service.register(username= user.username,
                                    email= user.email,
                                    password= user.password,
                                    db= db)
    return new_user



@router.post("/login",response_model= TokenResponse,status_code=status.HTTP_200_OK)
def login(formdata: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    
    token_response = auth_service.login(email= formdata.username,
                                        password= formdata.password,
                                        db= db)
    return token_response





@router.patch("/password_change",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def change_password(password: ChangePassword,
                    current_user:User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
     

     return auth_service.change_password(current_password= password.current_password,
                                         new_password= password.new_password,
                                         current_user= current_user,
                                         db= db)




@router.post("/verify_email",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def send_verification_code(current_user:User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
         
    return auth_service.send_verification_code(current_user,db)



     

@router.post("/verify_email/confirm",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def confirm_verification_code(verify: VerifyOTP ,
                           current_user:User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    

    return auth_service.confirm_verification_code(verification_otp= verify.otp,
                                                  current_user= current_user,
                                                  db= db)





@router.post("/forgot_password",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def forgot_password(email:ForgotPassword,
                 db: Session = Depends(get_db)):
     
     return auth_service.forgot_password(email= email.email,
                                         db= db)




@router.post("/reset_password",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def reset_password(reset: ResetPassword,
                   db: Session = Depends(get_db)):
    
    return auth_service.reset_password(email= reset.email,
                                       otp= reset.otp,
                                       new_password = reset.new_password,
                                       db= db)




@router.delete("/delete_account",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def delete_account(data: DeleteAccountRequest,
                   current_user:User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
         
     return auth_service.delete_account(password= data.password,
                                        current_user= current_user,
                                        db= db)