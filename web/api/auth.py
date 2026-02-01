"""Auth/Login API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import User, verify_password
from ..security import create_access_token, create_refresh_token, verify_access_token, verify_refresh_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    id: int
    name: str
    email: str
    access_token: str
    token_type: str = "bearer"
    message: str = "Login successful"
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str = "Token refreshed successfully"


class TokenPayload(BaseModel):
    user_id: int


@router.post("/login")
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login user with email and password and return JWT access token, refresh token in HttpOnly cookie"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT tokens
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    
    # Create response with access token in body
    response = JSONResponse(
        content={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Login successful"
        },
        status_code=200
    )
    
    # Set refresh token in HttpOnly cookie (15 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=15 * 24 * 60 * 60,  # 15 days in seconds
        httponly=True,
        secure=False,  # Set to True in production (HTTPS only)
        samesite="lax"
    )
    
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    # Verify refresh token
    user_id = verify_refresh_token(request.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new access token
    new_access_token = create_access_token(user_id=user_id)
    
    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.get("/logout")
async def logout():
    """Logout user by clearing refresh token cookie"""
    response = JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=200
    )
    
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    
    return response


@router.get("/verify-token", response_model=TokenPayload)
async def verify_token(token: str) -> TokenPayload:
    """Verify JWT access token and return user_id"""
    user_id = verify_access_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenPayload(user_id=user_id)

