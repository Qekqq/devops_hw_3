import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.config import get_path, get_project_root, load_config
from src.db.database import get_session_factory
from src.db.models import Dataset, DatasetSample
from src.features import FEATURE_COLUMNS, TARGET_COLUMN


def resolve_project_path(path_value: str) -> Path:
    """
    Преобразует путь из строки в абсолютный путь внутри проекта.

    Если путь уже абсолютный, возвращает его без изменений.
    Если путь относительный, строит его относительно корня проекта.
    """
    path = Path(path_value)

    if path.is_absolute():
        return path

    return get_project_root() / path


def parse_args() -> argparse.Namespace:
    """
    Читает аргументы командной строки.

    Если аргументы не переданы, значения будут взяты из config.ini.
    """
    parser = argparse.ArgumentParser(
        description="Загрузка обработанного датасета в PostgreSQL."
    )

    parser.add_argument("--dataset-name", default=None)
    parser.add_argument("--dataset-version", default=None)
    parser.add_argument("--source-path", default=None)

    parser.add_argument("--train-path", default=None)
    parser.add_argument("--valid-path", default=None)
    parser.add_argument("--test-path", default=None)

    return parser.parse_args()


def get_dataset_params(args: argparse.Namespace) -> dict[str, str]:
    """
    Получает параметры датасета из аргументов командной строки или config.ini.
    """
    config = load_config()

    dataset_name = args.dataset_name or config.get("dataset", "dataset_name")
    dataset_version = args.dataset_version or config.get("dataset", "dataset_version")
    source_path = args.source_path or config.get("dataset", "source_path")

    return {
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "source_path": source_path,
    }


def get_split_paths(args: argparse.Namespace) -> dict[str, Path]:
    """
    Получает пути к train/valid/test CSV-файлам.
    """
    config = load_config()

    train_path = (
        resolve_project_path(args.train_path)
        if args.train_path
        else get_path(config, "paths", "train_data_path")
    )

    valid_path = (
        resolve_project_path(args.valid_path)
        if args.valid_path
        else get_path(config, "paths", "valid_data_path")
    )

    test_path = (
        resolve_project_path(args.test_path)
        if args.test_path
        else get_path(config, "paths", "test_data_path")
    )

    return {
        "train": train_path,
        "valid": valid_path,
        "test": test_path,
    }


def get_or_create_dataset(
    db: Session,
    *,
    dataset_name: str,
    dataset_version: str,
    source_path: str,
) -> Dataset:
    """
    Создаёт запись о датасете или возвращает уже существующую.

    Пара dataset_name + dataset_version уникальна.
    """
    statement = select(Dataset).where(
        Dataset.dataset_name == dataset_name,
        Dataset.dataset_version == dataset_version,
    )

    dataset = db.execute(statement).scalar_one_or_none()

    if dataset is None:
        dataset = Dataset(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            source_path=source_path,
        )
        db.add(dataset)
        db.flush()
        return dataset

    dataset.source_path = source_path
    db.flush()

    return dataset


def validate_split_columns(data: pd.DataFrame, file_path: Path) -> None:
    """
    Проверяет, что CSV содержит все обязательные признаки и целевую колонку.
    """
    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"В файле {file_path} отсутствуют обязательные колонки: {missing_columns}"
        )


def load_split_file(
    *,
    file_path: Path,
    split_name: str,
    dataset_id: int,
) -> list[DatasetSample]:
    """
    Читает CSV-файл одного split и преобразует строки в ORM-объекты.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл split не найден: {file_path}")

    data = pd.read_csv(file_path)
    validate_split_columns(data, file_path)

    samples: list[DatasetSample] = []

    for row in data.to_dict(orient="records"):
        sample = DatasetSample(
            dataset_id=dataset_id,
            split=split_name,
            pregnancies=int(row["pregnancies"]),
            glucose=float(row["glucose"]),
            blood_pressure=float(row["blood_pressure"]),
            skin_thickness=float(row["skin_thickness"]),
            insulin=float(row["insulin"]),
            bmi=float(row["bmi"]),
            diabetes_pedigree_function=float(row["diabetes_pedigree_function"]),
            age=int(row["age"]),
            outcome=int(row["outcome"]),
        )
        samples.append(sample)

    return samples


def reload_dataset_samples(
    db: Session,
    *,
    dataset_id: int,
    split_paths: dict[str, Path],
) -> int:
    """
    Перезагружает строки dataset_samples для выбранного датасета.

    Старые строки удаляются, чтобы повторный запуск скрипта не создавал дубли.
    """
    db.execute(
        delete(DatasetSample).where(DatasetSample.dataset_id == dataset_id)
    )

    all_samples: list[DatasetSample] = []

    for split_name, file_path in split_paths.items():
        split_samples = load_split_file(
            file_path=file_path,
            split_name=split_name,
            dataset_id=dataset_id,
        )
        all_samples.extend(split_samples)

    db.add_all(all_samples)
    db.flush()

    return len(all_samples)


def run() -> None:
    """
    Загружает обработанные train/valid/test данные в PostgreSQL.
    """
    args = parse_args()

    dataset_params = get_dataset_params(args)
    split_paths = get_split_paths(args)

    source_path = str(resolve_project_path(dataset_params["source_path"]))

    session_factory = get_session_factory()

    with session_factory() as db:
        dataset = get_or_create_dataset(
            db,
            dataset_name=dataset_params["dataset_name"],
            dataset_version=dataset_params["dataset_version"],
            source_path=source_path,
        )

        loaded_rows = reload_dataset_samples(
            db,
            dataset_id=dataset.id,
            split_paths=split_paths,
        )

        db.commit()

    print(
        f"Датасет {dataset_params['dataset_name']}:{dataset_params['dataset_version']} "
        f"загружен в PostgreSQL. Количество строк: {loaded_rows}"
    )


if __name__ == "__main__":
    run()