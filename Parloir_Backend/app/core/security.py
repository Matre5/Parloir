from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import settings

# Use Argon2 instead of bcrypt (more modern, no Windows issues)
ph = PasswordHasher()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if password matches the hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def get_password_hash(password: str) -> str:
    """Hash a password for storing in database"""
    return ph.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token (short-lived - 30 minutes)"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token (long-lived - 30 days)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None



# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from app.core.config import settings

# # Password hashing setup - with truncation for bcrypt compatibility
# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto",
#     bcrypt__truncate_error=True  # Handle bcrypt version issues
# )

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Check if password matches the hash"""
#     # Truncate to 72 bytes for bcrypt
#     return pwd_context.verify(plain_password[:72], hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hash a password for storing in database"""
#     # Truncate to 72 bytes for bcrypt
#     return pwd_context.hash(password[:72])

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     """Create JWT access token (short-lived - 30 minutes)"""
#     to_encode = data.copy()
    
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

# def create_refresh_token(data: dict):
#     """Create JWT refresh token (long-lived - 30 days)"""
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

# def decode_token(token: str):
#     """Decode and verify JWT token"""
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         return payload
#     except JWTError:
#         return None