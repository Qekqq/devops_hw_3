import json

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from src.train import ModelTrainer


def test_trainer_loads_train_and_validation_data():
    trainer = ModelTrainer()

    train_data, valid_data = trainer.load_data()

    assert isinstance(train_data, pd.DataFrame)
    assert isinstance(valid_data, pd.DataFrame)

    assert not train_data.empty
    assert not valid_data.empty

    assert trainer.target_column in train_data.columns
    assert trainer.target_column in valid_data.columns


def test_split_features_and_target_removes_target_from_features():
    trainer = ModelTrainer()

    train_data, _ = trainer.load_data()

    X, y = trainer.split_features_and_target(train_data)

    assert trainer.target_column not in X.columns
    assert len(X) == len(y)
    assert len(X.columns) == 8


def test_build_model_returns_pipeline():
    trainer = ModelTrainer()

    model = trainer.build_model()

    assert isinstance(model, Pipeline)
    assert "scaler" in model.named_steps
    assert "classifier" in model.named_steps


def test_model_training_and_evaluation_returns_valid_metrics():
    trainer = ModelTrainer()

    train_data, valid_data = trainer.load_data()

    X_train, y_train = trainer.split_features_and_target(train_data)
    X_valid, y_valid = trainer.split_features_and_target(valid_data)

    model = trainer.build_model()
    model.fit(X_train, y_train)

    metrics = trainer.evaluate_model(model, X_valid, y_valid)

    expected_keys = {
        "model_name",
        "accuracy_score",
        "precision_score",
        "recall_score",
        "f1_score",
        "params",
    }

    assert expected_keys.issubset(metrics.keys())

    assert metrics["model_name"] == "LogisticRegressionTuned"
    assert 0 <= metrics["accuracy_score"] <= 1
    assert 0 <= metrics["precision_score"] <= 1
    assert 0 <= metrics["recall_score"] <= 1
    assert 0 <= metrics["f1_score"] <= 1


def test_save_model_and_metrics_creates_files(tmp_path):
    trainer = ModelTrainer()

    train_data, valid_data = trainer.load_data()

    X_train, y_train = trainer.split_features_and_target(train_data)
    X_valid, y_valid = trainer.split_features_and_target(valid_data)

    model = trainer.build_model()
    model.fit(X_train, y_train)

    metrics = trainer.evaluate_model(model, X_valid, y_valid)

    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "validation_metrics.json"

    trainer.best_model_path = model_path
    trainer.validation_metrics_path = metrics_path

    trainer.save_model_and_metrics(model, metrics)

    assert model_path.exists()
    assert metrics_path.exists()

    loaded_model = joblib.load(model_path)

    assert loaded_model is not None

    with open(metrics_path, "r", encoding="utf-8") as file:
        loaded_metrics = json.load(file)

    assert loaded_metrics["model_name"] == "LogisticRegressionTuned"
    assert "f1_score" in loaded_metrics