from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from models import SaveTransactionRequest
from app.services.jwt_service import verify_token
from app.services.s3_service import (
    upload_image_to_s3,
    generate_presigned_image_url
)
from app.services.dynamodb_service import (
    save_transaction_to_dynamodb,
    get_transactions_by_user,
    get_transaction_by_id
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

@router.get("/{transaction_id}/image-url")
def get_transaction_image_url(
    transaction_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        transaction = get_transaction_by_id(
            user_id=user_id,
            transaction_id=transaction_id
        )

        if transaction is None:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        image_s3_key = transaction.get("image_s3_key")

        if not image_s3_key:
            raise HTTPException(
                status_code=404,
                detail="Image not found for this transaction"
            )

        image_url = generate_presigned_image_url(
            image_s3_key=image_s3_key
        )

        return {
            "transaction_id": transaction_id,
            "image_s3_key": image_s3_key,
            "image_url": image_url
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )