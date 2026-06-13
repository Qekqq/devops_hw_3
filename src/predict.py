import joblib
import pandas as pd

from src.config import load_config, get_path, get_zero_as_missing_columns
from src.logger import get_logger


class DiabetesPredictor:
    """
    Класс для загрузки обученной модели и выполнения предсказаний.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = load_config()

        self.model_path = get_path(self.config, "paths", "best_model_path")
        self.train_data_path = get_path(self.config, "paths", "train_data_path")

        self.target_column = self.config.get("training", "target_column")
        self.zero_as_missing_columns = get_zero_as_missing_columns(self.config)

        self.model = self.load_model()
        self.feature_columns = self.get_feature_columns()
        self.train_medians = self.get_train_medians()

    def load_model(self):
        """
        Загружает финальную обученную модель.
        """
        self.logger.info("Loading model from %s", self.model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file was not found: {self.model_path}")

        model = joblib.load(self.model_path)

        self.logger.info("Model loaded successfully.")
        return model

    def get_feature_columns(self) -> list[str]:
        """
        Получает список признаков, которые нужны модели для предсказания.
        """
        if hasattr(self.model, "feature_names_in_"):
            feature_columns = list(self.model.feature_names_in_)
            self.logger.info("Feature columns loaded from model: %s", feature_columns)
            return feature_columns

        train_data = pd.read_csv(self.train_data_path)
        feature_columns = [
            column for column in train_data.columns
            if column != self.target_column
        ]

        self.logger.info("Feature columns loaded from train data: %s", feature_columns)
        return feature_columns

    def get_train_medians(self) -> dict[str, float]:
        """
        Рассчитывает медианы train-выборки для колонок, где нули считаются пропусками.
        """
        train_data = pd.read_csv(self.train_data_path)

        train_medians = (
            train_data[self.zero_as_missing_columns]
            .median()
            .to_dict()
        )

        self.logger.info("Train medians loaded: %s", train_medians)
        return train_medians

    def validate_input(self, input_data: dict) -> None:
        """
        Проверяет, что во входных данных есть все необходимые признаки.
        """
        missing_columns = [
            column for column in self.feature_columns
            if column not in input_data
        ]

        if missing_columns:
            raise ValueError(f"Missing input columns: {missing_columns}")

    def prepare_input(self, input_data: dict) -> pd.DataFrame:
        """
        Подготавливает входные данные к предсказанию.
        """
        self.validate_input(input_data)

        input_df = pd.DataFrame([input_data])
        input_df = input_df[self.feature_columns]

        for column in self.zero_as_missing_columns:
            if column in input_df.columns:
                input_df[column] = input_df[column].replace(
                    0,
                    self.train_medians[column],
                )

        return input_df

    def predict(self, input_data: dict) -> dict:
        """
        Выполняет предсказание для одного объекта.
        """
        self.logger.info("Prediction started.")

        input_df = self.prepare_input(input_data)

        prediction = int(self.model.predict(input_df)[0])

        probability = None
        if hasattr(self.model, "predict_proba"):
            probability = float(self.model.predict_proba(input_df)[0][1])

        result = {
            "prediction": prediction,
            "probability": probability,
            "label": "detected" if prediction == 1 else "not_detected",
        }

        self.logger.info("Prediction result: %s", result)

        return result


if __name__ == "__main__":
    example_input = {
        "Pregnancies": 6,
        "Glucose": 148,
        "BloodPressure": 72,
        "SkinThickness": 35,
        "Insulin": 0,
        "BMI": 33.6,
        "DiabetesPedigreeFunction": 0.627,
        "Age": 50,
    }

    predictor = DiabetesPredictor()
    result = predictor.predict(example_input)

    print(result)