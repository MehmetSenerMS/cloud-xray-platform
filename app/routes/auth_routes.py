from fastapi import APIRouter, HTTPException, status

from models import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from auth import create_user, authenticate_user
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(request: RegisterRequest):
    user = create_user(
        full_name=request.full_name,
        email=request.email,
        password=request.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return {
        "message": "User registered successfully",
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"]
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = authenticate_user(
        email=request.email,
        password=request.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {
        "sub": user["user_id"],
        "email": user["email"]
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    try:
        payload = verify_token(
            request.refresh_token,
            expected_token_type="refresh"
        )

        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email")
        }

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )