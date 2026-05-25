from passlib.context import CryptContext
import uuid

from app.utils.helpers import get_current_utc_datetime
from app.services.dynamodb_service import (
    USER_PROFILE_SORT_KEY,
    save_user_profile,
    get_user_by_email
)


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(full_name: str, email: str, password: str):
    existing_user = get_user_by_email(email)

    if existing_user:
        return None

    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)

    user_record = {
        "user_id": user_id,
        "transaction_id": USER_PROFILE_SORT_KEY,
        "record_type": "USER",
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "created_at": get_current_utc_datetime()
    }

    save_user_profile(user_record)

    return user_record


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return user