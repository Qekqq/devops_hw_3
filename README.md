# MLOps Diabetes Classification Project

Проект для лабораторной работы №1 по дисциплине "DevOps".

## Цель проекта

Разработать ML-сервис для бинарной классификации наличия диабета, реализовать API, покрыть код тестами, настроить DVC, Docker и CI/CD pipeline с использованием GitHub Actions.

## Dataset

Используется датасет `diabetes.csv`.

Задача: бинарная классификация.

Целевая переменная:

- `Outcome = 0` — диабет не обнаружен
- `Outcome = 1` — диабет обнаружен

## Модели

В проекте будут обучены и сравнены две классические модели машинного обучения:

1. LogisticRegression
2. DecisionTreeClassifier

Финальная модель выбирается по значению F1-score.

## Стек

- Python
- pandas
- scikit-learn
- FastAPI
- pytest
- DVC
- Docker
- Docker Compose
- GitHub Actions

## Структура проекта

```
data/raw/              исходные данные
data/processed/        обработанные данные
src/                   исходный код проекта
tests/                 тесты
experiments/           результаты экспериментов с моделями
notebooks/             исследовательские ноутбуки
reports/               материалы для отчёта
.github/workflows/     CI/CD pipeline