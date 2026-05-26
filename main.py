from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.prediction_routes import router as prediction_router
from app.routes.transaction_routes import router as transaction_router


app = FastAPI(
    title="Cloud X-Ray Platform API",
    version="1.0.0",
    root_path="/prod"
)

app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(transaction_router)


@app.get("/")
def root():
    return {
        "message": "Cloud X-Ray Platform API is running"
    }