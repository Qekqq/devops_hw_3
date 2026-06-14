import pytest

from src.predict import DiabetesPredictor


VALID_INPUT = {
    "pregnancies": 6,
    "glucose": 148,
    "blood_pressure": 72,
    "skin_thickness": 35,
    "insulin": 0,
    "bmi": 33.6,
    "diabetes_pedigree_function": 0.627,
    "age": 50,
}


def test_predictor_loads_model_successfully():
    predictor = DiabetesPredictor()

    assert predictor.model is not None
    assert predictor.model_path.exists()


def test_predictor_has_expected_feature_columns():
    predictor = DiabetesPredictor()

    expected_columns = [
        "pregnancies",
        "glucose",
        "blood_pressure",
        "skin_thickness",
        "insulin",
        "bmi",
        "diabetes_pedigree_function",
        "age",
    ]

    assert predictor.feature_columns == expected_columns


def test_prepare_input_replaces_zero_values_with_train_medians():
    predictor = DiabetesPredictor()

    prepared_input = predictor.prepare_input(VALID_INPUT)

    assert prepared_input.shape == (1, 8)

    assert prepared_input.loc[0, "insulin"] == predictor.train_medians["insulin"]


def test_predict_returns_valid_result():
    predictor = DiabetesPredictor()

    result = predictor.predict(VALID_INPUT)

    assert "prediction" in result
    assert "probability" in result
    assert "label" in result

    assert result["prediction"] in [0, 1]
    assert result["label"] in ["detected", "not_detected"]

    if result["probability"] is not None:
        assert 0 <= result["probability"] <= 1


def test_predict_raises_error_for_missing_column():
    predictor = DiabetesPredictor()

    invalid_input = VALID_INPUT.copy()
    invalid_input.pop("age")

    with pytest.raises(ValueError, match="Missing input columns"):
        predictor.predict(invalid_input)