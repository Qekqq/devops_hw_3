import pandas as pd

from src.data_preprocessing import DataPreprocessor


def create_test_dataframe() -> pd.DataFrame:
    """
    Создаёт небольшой тестовый датасет с той же структурой, что и diabetes.csv.
    """
    rows = []

    for index in range(100):
        rows.append(
            {
                "pregnancies": index % 5,
                "glucose": 100 + index,
                "blood_pressure": 60 + index % 30,
                "skin_thickness": 20 + index % 20,
                "insulin": 80 + index,
                "bmi": 25.0 + index % 10,
                "diabetes_pedigree_function": 0.1 + index / 1000,
                "age": 20 + index % 50,
                "outcome": index % 2,
            }
        )

    return pd.DataFrame(rows)


def test_load_data_returns_dataframe_with_target_column():
    preprocessor = DataPreprocessor()

    df = preprocessor.load_data()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert preprocessor.target_column in df.columns


def test_split_data_preserves_total_number_of_rows():
    preprocessor = DataPreprocessor()
    df = create_test_dataframe()

    X_train, X_valid, X_test, y_train, y_valid, y_test = preprocessor.split_data(df)

    total_features_rows = len(X_train) + len(X_valid) + len(X_test)
    total_target_rows = len(y_train) + len(y_valid) + len(y_test)

    assert total_features_rows == len(df)
    assert total_target_rows == len(df)

    assert preprocessor.target_column not in X_train.columns
    assert preprocessor.target_column not in X_valid.columns
    assert preprocessor.target_column not in X_test.columns


def test_replace_zero_values_with_train_medians():
    preprocessor = DataPreprocessor()

    X_train = pd.DataFrame(
        {
            "pregnancies": [0, 1, 2],
            "glucose": [0, 100, 120],
            "blood_pressure": [0, 70, 80],
            "skin_thickness": [0, 20, 40],
            "insulin": [0, 100, 200],
            "bmi": [0, 30.0, 40.0],
            "diabetes_pedigree_function": [0.1, 0.2, 0.3],
            "age": [25, 35, 45],
        }
    )

    X_valid = pd.DataFrame(
        {
            "pregnancies": [1],
            "glucose": [0],
            "blood_pressure": [0],
            "skin_thickness": [0],
            "insulin": [0],
            "bmi": [0],
            "diabetes_pedigree_function": [0.4],
            "age": [50],
        }
    )

    X_test = X_valid.copy()

    X_train_processed, X_valid_processed, X_test_processed = (
        preprocessor.replace_zero_values_with_train_medians(
            X_train=X_train,
            X_valid=X_valid,
            X_test=X_test,
        )
    )

    assert X_valid_processed.loc[0, "glucose"] == 110.0
    assert X_valid_processed.loc[0, "blood_pressure"] == 75.0
    assert X_valid_processed.loc[0, "skin_thickness"] == 30.0
    assert X_valid_processed.loc[0, "insulin"] == 150.0
    assert X_valid_processed.loc[0, "bmi"] == 35.0

    for column in preprocessor.zero_as_missing_columns:
        assert X_train_processed[column].isna().sum() == 0
        assert X_valid_processed[column].isna().sum() == 0
        assert X_test_processed[column].isna().sum() == 0


def test_combine_features_and_target_adds_target_column():
    preprocessor = DataPreprocessor()

    X = pd.DataFrame(
        {
            "glucose": [120, 140],
            "bmi": [30.0, 35.0],
        }
    )

    y = pd.Series([0, 1], name=preprocessor.target_column)

    combined_data = preprocessor.combine_features_and_target(X, y)

    assert preprocessor.target_column in combined_data.columns
    assert combined_data.shape == (2, 3)
    assert combined_data[preprocessor.target_column].tolist() == [0, 1]