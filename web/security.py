"""JWT Token utilities"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

# Get secret key from environment
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_MINUTES = 24 * 60  # 24 hours
REFRESH_TOKEN_EXPIRATION_DAYS = 15  # 15 days


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with user_id and expiration"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token with user_id and 15-day expiration"""
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[int]:
    """Verify JWT access token and return user_id if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        
        # Verify token type is access
        if token_type != "access":
            return None
        
        if user_id is None:
            return None
        
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token: str) -> Optional[int]:
    """Verify JWT refresh token and return user_id if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        
        # Verify token type is refresh
        if token_type != "refresh":
            return None
        
        if user_id is None:
            return None
        
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

