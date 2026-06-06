from fastapi import FastAPI, HTTPException

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