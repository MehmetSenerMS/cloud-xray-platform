from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from models import SaveTransactionRequest
from app.services.jwt_service import verify_token


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

security = HTTPBearer()

# Temporary in-memory transaction storage
# Later we will replace this with DynamoDB
transactions_db = []


@router.post("/save")
def save_transaction(
    request: SaveTransactionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        transaction_record = {
            "transaction_id": request.transaction_id,
            "transaction_date": request.transaction_date,
            "user_id": user_id,
            "image_base64": request.image_base64,
            "result": request.result
        }

        transactions_db.append(transaction_record)

        return {
            "message": "Transaction saved successfully",
            "transaction": transaction_record
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/history")
def get_transaction_history(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        user_transactions = [
            transaction
            for transaction in transactions_db
            if transaction["user_id"] == user_id
        ]

        return {
            "user_id": user_id,
            "count": len(user_transactions),
            "transactions": user_transactions
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )