import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import load_config, get_path, get_zero_as_missing_columns
from src.logger import get_logger


class DataPreprocessor:
    """
    Класс для подготовки данных к обучению модели.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.config = load_config()

        self.raw_data_path = get_path(self.config, "paths", "raw_data_path")
        self.train_data_path = get_path(self.config, "paths", "train_data_path")
        self.valid_data_path = get_path(self.config, "paths", "valid_data_path")
        self.test_data_path = get_path(self.config, "paths", "test_data_path")

        self.target_column = self.config.get("training", "target_column")
        self.train_size = self.config.getfloat("training", "train_size")
        self.valid_size = self.config.getfloat("training", "valid_size")
        self.test_size = self.config.getfloat("training", "test_size")
        self.random_state = self.config.getint("training", "random_state")

        self.zero_as_missing_columns = get_zero_as_missing_columns(self.config)

    def load_data(self) -> pd.DataFrame:
        """
        Загружает исходный датасет.
        """
        self.logger.info("Loading raw dataset from %s", self.raw_data_path)

        if not self.raw_data_path.exists():
            raise FileNotFoundError(f"Raw dataset was not found: {self.raw_data_path}")

        df = pd.read_csv(self.raw_data_path)

        self.logger.info("Raw dataset loaded successfully. Shape: %s", df.shape)
        return df

    def split_data(
        self,
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Делит данные на train, validation и test выборки со стратификацией по целевой переменной.
        """
        split_sum = self.train_size + self.valid_size + self.test_size

        if round(split_sum, 5) != 1.0:
            raise ValueError("Sum of train_size, valid_size and test_size must be equal to 1.0")

        self.logger.info(
            "Splitting data. Train: %.2f, valid: %.2f, test: %.2f",
            self.train_size,
            self.valid_size,
            self.test_size,
        )

        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]

        X_train_valid, X_test, y_train_valid, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y,
        )

        valid_size_from_train_valid = self.valid_size / (self.train_size + self.valid_size)

        X_train, X_valid, y_train, y_valid = train_test_split(
            X_train_valid,
            y_train_valid,
            test_size=valid_size_from_train_valid,
            random_state=self.random_state,
            stratify=y_train_valid,
        )

        self.logger.info("Train shape: %s", X_train.shape)
        self.logger.info("Validation shape: %s", X_valid.shape)
        self.logger.info("Test shape: %s", X_test.shape)

        return X_train, X_valid, X_test, y_train, y_valid, y_test

    def replace_zero_values_with_train_medians(
        self,
        X_train: pd.DataFrame,
        X_valid: pd.DataFrame,
        X_test: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Заменяет некорректные нулевые значения на медианы, рассчитанные только на train-выборке.
        """
        self.logger.info(
            "Replacing zero values with train medians for columns: %s",
            self.zero_as_missing_columns,
        )

        X_train_processed = X_train.copy()
        X_valid_processed = X_valid.copy()
        X_test_processed = X_test.copy()

        for dataset in [X_train_processed, X_valid_processed, X_test_processed]:
            dataset[self.zero_as_missing_columns] = dataset[self.zero_as_missing_columns].replace(
                0,
                np.nan,
            )

        train_medians = X_train_processed[self.zero_as_missing_columns].median()

        self.logger.info("Train medians calculated: %s", train_medians.to_dict())

        for dataset in [X_train_processed, X_valid_processed, X_test_processed]:
            dataset[self.zero_as_missing_columns] = dataset[self.zero_as_missing_columns].fillna(
                train_medians,
            )

        return X_train_processed, X_valid_processed, X_test_processed

    def combine_features_and_target(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> pd.DataFrame:
        """
        Объединяет признаки и целевую переменную в один DataFrame.
        """
        data = X.copy()
        data[self.target_column] = y
        return data

    def save_processed_data(
        self,
        train_data: pd.DataFrame,
        valid_data: pd.DataFrame,
        test_data: pd.DataFrame,
    ) -> None:
        """
        Сохраняет обработанные train, validation и test выборки в CSV-файлы.
        """
        self.train_data_path.parent.mkdir(parents=True, exist_ok=True)

        train_data.to_csv(self.train_data_path, index=False)
        valid_data.to_csv(self.valid_data_path, index=False)
        test_data.to_csv(self.test_data_path, index=False)

        self.logger.info("Train data saved to %s", self.train_data_path)
        self.logger.info("Validation data saved to %s", self.valid_data_path)
        self.logger.info("Test data saved to %s", self.test_data_path)

    def run(self) -> None:
        """
        Запускает полный пайплайн предобработки данных.
        """
        self.logger.info("Data preprocessing started.")

        df = self.load_data()

        X_train, X_valid, X_test, y_train, y_valid, y_test = self.split_data(df)

        X_train_processed, X_valid_processed, X_test_processed = (
            self.replace_zero_values_with_train_medians(
                X_train=X_train,
                X_valid=X_valid,
                X_test=X_test,
            )
        )

        train_data = self.combine_features_and_target(X_train_processed, y_train)
        valid_data = self.combine_features_and_target(X_valid_processed, y_valid)
        test_data = self.combine_features_and_target(X_test_processed, y_test)

        self.save_processed_data(
            train_data=train_data,
            valid_data=valid_data,
            test_data=test_data,
        )

        self.logger.info("Data preprocessing finished successfully.")


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.run()