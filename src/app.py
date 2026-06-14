import time

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.db.database import get_session_factory
from src.db.repositories import require_champion_model, save_prediction_history
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


def build_db_features(input_data: DiabetesInput) -> dict[str, float | int]:
    """
    Преобразует входные данные API в словарь признаков для сохранения в БД.
    """
    return {
        "pregnancies": input_data.pregnancies,
        "glucose": input_data.glucose,
        "blood_pressure": input_data.blood_pressure,
        "skin_thickness": input_data.skin_thickness,
        "insulin": input_data.insulin,
        "bmi": input_data.bmi,
        "diabetes_pedigree_function": input_data.diabetes_pedigree_function,
        "age": input_data.age,
    }


def save_prediction_to_database(
    input_data: DiabetesInput,
    result: dict,
    response_time_ms: int,
) -> None:
    """
    Сохраняет результат прогноза в PostgreSQL.

    Если БД недоступна, API всё равно возвращает результат прогноза.
    Это позволяет unit-тестам API работать без запущенного PostgreSQL.
    """
    try:
        session_factory = get_session_factory()

        with session_factory() as db:
            model_version = require_champion_model(db)

            save_prediction_history(
                db=db,
                features=build_db_features(input_data),
                prediction=result["prediction"],
                probability=result.get("probability"),
                model_version=model_version,
                patient_code=input_data.patient_code,
                request_source="api",
                response_time_ms=response_time_ms,
            )

            db.commit()

    except (RuntimeError, SQLAlchemyError) as error:
        logger.error("Не удалось сохранить прогноз в БД: %s", error)


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
    Проверяет подключение API к PostgreSQL.
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
        logger.error("Проверка подключения к БД завершилась ошибкой: %s", error)
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.post("/predict", response_model=PredictionResponse)
def predict_diabetes(input_data: DiabetesInput) -> PredictionResponse:
    """
    Выполняет прогноз риска диабета и сохраняет результат в БД.
    """
    start_time = time.perf_counter()

    try:
        model_input = input_data.model_dump(exclude={"patient_code"})
        result = predictor.predict(model_input)

        response_time_ms = int((time.perf_counter() - start_time) * 1000)

        save_prediction_to_database(
            input_data=input_data,
            result=result,
            response_time_ms=response_time_ms,
        )

        return PredictionResponse(**result)

    except ValueError as error:
        logger.error("Ошибка валидации при выполнении прогноза: %s", error)
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.error("Непредвиденная ошибка при выполнении прогноза: %s", error)
        raise HTTPException(status_code=500, detail="Internal server error")