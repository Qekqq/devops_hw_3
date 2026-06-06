from pydantic import BaseModel, Field


class DiabetesInput(BaseModel):
    """
    Схема входных данных для предсказания диабета.
    """

    Pregnancies: int = Field(..., ge=0, description="Количество беременностей")
    Glucose: float = Field(..., ge=0, description="Уровень глюкозы")
    BloodPressure: float = Field(..., ge=0, description="Артериальное давление")
    SkinThickness: float = Field(..., ge=0, description="Толщина кожной складки")
    Insulin: float = Field(..., ge=0, description="Уровень инсулина")
    BMI: float = Field(..., ge=0, description="Индекс массы тела")
    DiabetesPedigreeFunction: float = Field(..., ge=0, description="Наследственный фактор диабета")
    Age: int = Field(..., ge=0, description="Возраст")


class PredictionResponse(BaseModel):
    """
    Схема ответа API с результатом предсказания.
    """

    prediction: int = Field(..., description="Класс предсказания: 0 или 1")
    probability: float | None = Field(None, description="Вероятность положительного класса")
    label: str = Field(..., description="Текстовая интерпретация результата")


class HealthResponse(BaseModel):
    """
    Схема ответа для проверки состояния API.
    """

    status: str
    service: str