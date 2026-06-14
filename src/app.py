from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.db.database import get_session_factory
from src.logger import get_logger
from src.predict import DiabetesPredictor
from src.schemas import DiabetesInput, HealthResponse, PredictionResponse


logger = get_logger(__name__)

app = FastAPI(
    title="Diabetes Prediction API",
    description="API для предсказания наличия диабета на основе медицинских признаков.",
    version="1.0.0",
)

predictor = DiabetesPredictor()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Проверяет состояние API.
    """
    return HealthResponse(
        status="ok",
        service="diabetes-prediction-api",
    )


@app.get("/db/health")
def database_health_check() -> dict[str, str]:
    """
    Проверяет соединение API с PostgreSQL.
    """
    try:
        session_factory = get_session_factory()

        with session_factory() as db:
            db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except (RuntimeError, SQLAlchemyError) as error:
        logger.error("Database health check failed: %s", error)
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )


@app.post("/predict", response_model=PredictionResponse)
def predict_diabetes(input_data: DiabetesInput) -> PredictionResponse:
    """
    Выполняет предсказание наличия диабета.
    """
    try:
        input_dict = input_data.model_dump()
        result = predictor.predict(input_dict)

        return PredictionResponse(**result)

    except ValueError as error:
        logger.error("Validation error during prediction: %s", error)
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.error("Unexpected error during prediction: %s", error)
        raise HTTPException(status_code=500, detail="Internal server error")