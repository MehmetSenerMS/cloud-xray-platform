from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: EmailStr


class PredictRequest(BaseModel):
    image_base64: str


class PredictResponse(BaseModel):
    transaction_id: str
    transaction_date: str
    result: Dict[str, Any]


class SaveTransactionRequest(BaseModel):
    transaction_id: str
    transaction_date: str
    image_base64: str
    prediction_result: Dict[str, Any]
    inference_duration_seconds: Optional[float] = None


class TransactionResponse(BaseModel):
    transaction_id: str
    transaction_date: str
    user_id: str
    image_base64: str
    result: Dict[str, Any]