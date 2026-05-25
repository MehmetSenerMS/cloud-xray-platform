from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from models import PredictRequest
from app.services.prediction_service import run_prediction
from app.services.jwt_service import verify_token
from app.utils.helpers import generate_transaction_id, get_current_utc_datetime

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)

security = HTTPBearer()

@router.post("/predict")
def predict(
    request: PredictRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        prediction_result = run_prediction(request.image_base64)

        transaction_id = generate_transaction_id()
        transaction_date = get_current_utc_datetime()

        return {
            "transaction_id": transaction_id,
            "transaction_date": transaction_date,
            "user_id": user_id,
            "prediction_result": prediction_result
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