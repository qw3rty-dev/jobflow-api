from datetime import datetime,timedelta, UTC

from pwdlib import PasswordHash
import secrets

password_hash = PasswordHash.recommended()

def hash_password(password:str) -> str:
    hashed_password = password_hash.hash(password)
    return hashed_password

def verify_password(plain_password: str, hashed_password:str) -> bool:
    
    return password_hash.verify(plain_password,hashed_password)


def verification_code_generate():

    verification_code = str(secrets.randbelow(900000)+100000)
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    return verification_code,expires_at
