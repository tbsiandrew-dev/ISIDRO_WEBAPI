"""Dependencies for route protection"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials
from .security import verify_access_token

security = HTTPBearer()


async def get_current_user(credentials = Depends(security)) -> int:
    """
    Dependency to verify JWT token from Authorization header
    Returns user_id if token is valid
    """
    token = credentials.credentials
    user_id = verify_access_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id
