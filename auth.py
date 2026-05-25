from passlib.context import CryptContext
import uuid


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# Temporary in-memory user storage
# Later we will replace this with DynamoDB
fake_users_db = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(full_name: str, email: str, password: str):
    
    if email in fake_users_db:
        return None

    user_id = str(uuid.uuid4())

    hashed_password = hash_password(password)

    user_data = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_password
    }

    fake_users_db[email] = user_data

    return user_data


def authenticate_user(email: str, password: str):

    user = fake_users_db.get(email)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return user