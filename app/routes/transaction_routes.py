from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from models import SaveTransactionRequest
from app.services.jwt_service import verify_token
from app.services.s3_service import upload_image_to_s3
from app.services.dynamodb_service import (
    save_transaction_to_dynamodb,
    get_transactions_by_user
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

security = HTTPBearer()


@router.post("/save")
def save_transaction(
    request: SaveTransactionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        image_s3_key = upload_image_to_s3(
            base64_image=request.image_base64,
            user_id=user_id,
            transaction_id=request.transaction_id
        )

        transaction_record = {
            "user_id": user_id,
            "transaction_id": request.transaction_id,
            "transaction_date": request.transaction_date,
            "image_s3_key": image_s3_key,
            "result": request.result
        }

        saved_transaction = save_transaction_to_dynamodb(
            transaction_record
        )

        return {
            "message": "Transaction saved successfully",
            "transaction": saved_transaction
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

        user_transactions = get_transactions_by_user(user_id)

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