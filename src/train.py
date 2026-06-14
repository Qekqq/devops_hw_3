import json

import joblib
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import load_config, get_path
from src.logger import get_logger


class ModelTrainer:
    """
    Класс для обучения финальной модели классификации диабета.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = load_config()

        self.train_data_path = get_path(self.config, "paths", "train_data_path")
        self.valid_data_path = get_path(self.config, "paths", "valid_data_path")
        self.best_model_path = get_path(self.config, "paths", "best_model_path")
        self.validation_metrics_path = get_path(
            self.config,
            "paths",
            "best_validation_metrics_path",
        )

        self.target_column = self.config.get("training", "target_column")
        self.random_state = self.config.getint("training", "random_state")
        self.selected_model_name = self.config.get("model", "selected_model_name")

    def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Загружает train и validation датасеты.
        """
        self.logger.info("Loading train data from %s", self.train_data_path)
        self.logger.info("Loading validation data from %s", self.valid_data_path)

        if not self.train_data_path.exists():
            raise FileNotFoundError(f"Train data was not found: {self.train_data_path}")

        if not self.valid_data_path.exists():
            raise FileNotFoundError(f"Validation data was not found: {self.valid_data_path}")

        train_data = pd.read_csv(self.train_data_path)
        valid_data = pd.read_csv(self.valid_data_path)

        self.logger.info("Train data shape: %s", train_data.shape)
        self.logger.info("Validation data shape: %s", valid_data.shape)

        return train_data, valid_data

    def split_features_and_target(
        self,
        data: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Разделяет датасет на признаки и целевую переменную.
        """
        X = data.drop(columns=[self.target_column])
        y = data[self.target_column]

        return X, y

    def build_model(self) -> Pipeline:
        """
        Создаёт финальную модель LogisticRegressionTuned.
        """
        if self.selected_model_name != "LogisticRegressionTuned":
            raise ValueError(
                f"Unsupported selected model: {self.selected_model_name}. "
                "Only LogisticRegressionTuned is supported in train.py."
            )

        model = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        C=1,
                        penalty="l1",
                        class_weight="balanced",
                        solver="liblinear",
                        max_iter=1000,
                        random_state=self.random_state,
                    ),
                ),
            ]
        )

        self.logger.info("Model created: %s", self.selected_model_name)
        return model

    def evaluate_model(
        self,
        model: Pipeline,
        X_valid: pd.DataFrame,
        y_valid: pd.Series,
    ) -> dict:
        """
        Оценивает модель на validation-выборке.
        """
        y_pred = model.predict(X_valid)

        metrics = {
            "model_name": self.selected_model_name,
            "accuracy_score": float(accuracy_score(y_valid, y_pred)),
            "precision_score": float(precision_score(y_valid, y_pred)),
            "recall_score": float(recall_score(y_valid, y_pred)),
            "f1_score": float(f1_score(y_valid, y_pred)),
            "params": {
                "C": 1,
                "penalty": "l1",
                "class_weight": "balanced",
                "solver": "liblinear",
                "max_iter": 1000,
            },
        }

        self.logger.info("Validation metrics: %s", metrics)
        return metrics

    def save_model_and_metrics(
        self,
        model: Pipeline,
        metrics: dict,
    ) -> None:
        """
        Сохраняет обученную модель и validation-метрики.
        """
        self.best_model_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(model, self.best_model_path)

        with open(self.validation_metrics_path, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        self.logger.info("Model saved to %s", self.best_model_path)
        self.logger.info("Validation metrics saved to %s", self.validation_metrics_path)

    def run(self) -> None:
        """
        Запускает полный pipeline обучения финальной модели.
        """
        self.logger.info("Model training started.")

        train_data, valid_data = self.load_data()

        X_train, y_train = self.split_features_and_target(train_data)
        X_valid, y_valid = self.split_features_and_target(valid_data)

        model = self.build_model()

        self.logger.info("Fitting model...")
        model.fit(X_train, y_train)
        self.logger.info("Model fitted successfully.")

        metrics = self.evaluate_model(model, X_valid, y_valid)

        self.save_model_and_metrics(model, metrics)

        self.logger.info("Model training finished successfully.")


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()