from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


VALID_INPUT = {
    "Pregnancies": 6,
    "Glucose": 148,
    "BloodPressure": 72,
    "SkinThickness": 35,
    "Insulin": 0,
    "BMI": 33.6,
    "DiabetesPedigreeFunction": 0.627,
    "Age": 50,
}


def test_health_check_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "diabetes-prediction-api"


def test_predict_returns_valid_prediction():
    response = client.post("/predict", json=VALID_INPUT)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert "label" in data

    assert data["prediction"] in [0, 1]
    assert data["label"] in ["detected", "not_detected"]

    if data["probability"] is not None:
        assert 0 <= data["probability"] <= 1


def test_predict_returns_422_for_missing_required_field():
    invalid_input = VALID_INPUT.copy()
    invalid_input.pop("Age")

    response = client.post("/predict", json=invalid_input)

    assert response.status_code == 422


def test_predict_returns_422_for_negative_value():
    invalid_input = VALID_INPUT.copy()
    invalid_input["Glucose"] = -1

    response = client.post("/predict", json=invalid_input)

    assert response.status_code == 422


def test_predict_returns_422_for_invalid_type():
    invalid_input = VALID_INPUT.copy()
    invalid_input["Age"] = "fifty"

    response = client.post("/predict", json=invalid_input)

    assert response.status_code == 422


def test_unknown_endpoint_returns_404():
    response = client.get("/unknown")

    assert response.status_code == 404