import time
from app.services.cloudwatch_service import put_metric
from app.utils.logger import logger
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
        start_time = time.time()

        logger.info("Prediction request received")

        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")

        prediction_result = run_prediction(request.image_base64)

        transaction_id = generate_transaction_id()
        transaction_date = get_current_utc_datetime()

        end_time = time.time()
        prediction_duration = round(end_time - start_time, 4)

        logger.info(
            f"Prediction completed successfully | "
            f"user_id={user_id} | "
            f"transaction_id={transaction_id} | "
            f"duration={prediction_duration}s"
        )
        
        put_metric(
            metric_name="InferenceDuration",
            value=prediction_duration,
            unit="Seconds"
            )

        return {
            "transaction_id": transaction_id,
            "transaction_date": transaction_date,
            "user_id": user_id,
            "prediction_result": prediction_result,
            "inference_duration_seconds": prediction_duration
        }

    except JWTError:
        logger.error("Prediction failed | invalid JWT token")

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Prediction failed | error={str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )