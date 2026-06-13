from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import (
    ModelVersion,
    Patient,
    PredictionFeedback,
    PredictionHistory,
)


def get_champion_model(db: Session) -> ModelVersion | None:
    """
    Возвращает текущую champion-модель.

    В БД по ограничению uq_model_versions_single_champion
    может быть только одна модель с role = 'champion'.
    """
    statement = select(ModelVersion).where(ModelVersion.role == "champion")
    return db.execute(statement).scalar_one_or_none()


def require_champion_model(db: Session) -> ModelVersion:
    """
    Возвращает champion-модель или выбрасывает ошибку,
    если она не заведена в model_versions.
    """
    model_version = get_champion_model(db)

    if model_version is None:
        raise RuntimeError("Champion model version was not found in database")

    return model_version


def get_patient_by_code(db: Session, patient_code: str) -> Patient | None:
    """
    Ищет пациента по коду.
    """
    normalized_code = patient_code.strip()

    statement = select(Patient).where(Patient.patient_code == normalized_code)
    return db.execute(statement).scalar_one_or_none()


def get_or_create_patient(db: Session, patient_code: str | None) -> Patient | None:
    """
    Возвращает существующего пациента или создаёт нового.

    Если patient_code не передан, возвращает None.
    Это допустимо, потому что prediction_history.patient_id может быть NULL.
    """
    if patient_code is None:
        return None

    normalized_code = patient_code.strip()

    if not normalized_code:
        return None

    patient = get_patient_by_code(db, normalized_code)

    if patient is not None:
        return patient

    patient = Patient(patient_code=normalized_code)
    db.add(patient)
    db.flush()

    return patient


def save_prediction_history(
    db: Session,
    *,
    features: dict[str, Any],
    prediction: int,
    probability: float | None,
    model_version: ModelVersion,
    patient_code: str | None = None,
    user_id: int | None = None,
    request_source: str = "api",
    response_time_ms: int | None = None,
) -> PredictionHistory:
    """
    Сохраняет одно предсказание в prediction_history.

    Важно:
    - commit здесь не вызывается;
    - commit будет делать endpoint/service-слой;
    - это позволяет сохранить несколько связанных действий одной транзакцией.
    """
    patient = get_or_create_patient(db, patient_code)

    label = "detected" if int(prediction) == 1 else "not_detected"

    prediction_history = PredictionHistory(
        user_id=user_id,
        patient_id=patient.id if patient is not None else None,
        model_version_id=model_version.id,
        patient_code_snapshot=patient.patient_code if patient is not None else None,
        model_version_snapshot=model_version.model_version,
        pregnancies=features["pregnancies"],
        glucose=features["glucose"],
        blood_pressure=features["blood_pressure"],
        skin_thickness=features["skin_thickness"],
        insulin=features["insulin"],
        bmi=features["bmi"],
        diabetes_pedigree_function=features["diabetes_pedigree_function"],
        age=features["age"],
        prediction=int(prediction),
        probability=probability,
        label=label,
        request_source=request_source,
        response_time_ms=response_time_ms,
    )

    db.add(prediction_history)
    db.flush()

    return prediction_history


def get_prediction_history_by_id(
    db: Session,
    prediction_history_id: int,
) -> PredictionHistory | None:
    """
    Возвращает запись истории предсказания по id.
    """
    statement = select(PredictionHistory).where(
        PredictionHistory.id == prediction_history_id
    )
    return db.execute(statement).scalar_one_or_none()


def save_prediction_feedback(
    db: Session,
    *,
    prediction_history_id: int,
    true_label: int,
    created_by_user_id: int | None = None,
) -> PredictionFeedback:
    """
    Создаёт или обновляет feedback по предсказанию.

    В prediction_feedback есть UNIQUE(prediction_history_id),
    поэтому на одно предсказание может быть только одна истинная метка.
    """
    if true_label not in (0, 1):
        raise ValueError("true_label must be 0 or 1")

    statement = select(PredictionFeedback).where(
        PredictionFeedback.prediction_history_id == prediction_history_id
    )
    feedback = db.execute(statement).scalar_one_or_none()

    if feedback is None:
        feedback = PredictionFeedback(
            prediction_history_id=prediction_history_id,
            true_label=true_label,
            created_by_user_id=created_by_user_id,
        )
        db.add(feedback)
    else:
        feedback.true_label = true_label
        feedback.created_by_user_id = created_by_user_id

    db.flush()

    return feedback