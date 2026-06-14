# MLOps Diabetes Prediction API

Проект выполнен в рамках лабораторной работы по модулю **DevOps**.

Цель проекта — разработать ML-модель для бинарной классификации наличия диабета, оформить код в виде воспроизводимого пайплайна, реализовать API-сервис для получения предсказаний, покрыть проект тестами, контейнеризировать приложение с помощью Docker и настроить CI/CD pipeline.

## Ссылки

* GitHub repository: https://github.com/Qekqq/mloops
* DockerHub image: https://hub.docker.com/r/qekqq/mloops_api

## Стек технологий

* Python 3.11
* pandas
* numpy
* scikit-learn
* FastAPI
* Uvicorn
* pytest
* DVC
* Docker
* Docker Compose
* GitHub Actions
* DockerHub

## Структура проекта

```text
.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── data/
│   ├── raw/
│   │   └── diabetes.csv
│   └── processed/
│       ├── train.csv
│       ├── valid.csv
│       └── test.csv
├── experiments/
│   ├── best_model/
│   │   ├── model.joblib
│   │   ├── validation_metrics.json
│   │   └── test_metrics.json
│   ├── logistic_regression_tuned/
│   └── decision_tree_tuned/
├── notebooks/
│   ├── 01_eda_preprocessing_split.ipynb
│   ├── 04_hyperparameter_tuning.ipynb
│   └── 05_model_comparison.ipynb
├── src/
│   ├── app.py
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── logger.py
│   ├── predict.py
│   ├── schemas.py
│   └── train.py
├── tests/
│   ├── test_api.py
│   ├── test_data_preprocessing.py
│   ├── test_predict.py
│   └── test_train.py
├── config.ini
├── dvc.yaml
├── dvc.lock
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md
```

## Описание ML-задачи

В проекте решается задача бинарной классификации: определить наличие диабета у пациента на основе медицинских признаков.

Целевая переменная:

```text
Outcome
```

Классы:

```text
0 — not_detected
1 — detected
```

Используемые признаки:

```text
Pregnancies
Glucose
BloodPressure
SkinThickness
Insulin
BMI
DiabetesPedigreeFunction
Age
```

## Подготовка данных

Подготовка данных реализована в модуле:

```text
src/data_preprocessing.py
```

Основные шаги:

* загрузка исходного датасета;
* разделение на train / validation / test;
* обработка нулевых значений в медицинских признаках;
* замена нулевых значений медианами, рассчитанными по train-выборке;
* сохранение обработанных данных в `data/processed`.

Запуск:

```bash
python -m src.data_preprocessing
```

## Обучение модели

Обучение модели реализовано в модуле:

```text
src/train.py
```

В качестве итоговой модели используется:

```text
LogisticRegressionTuned
```

Модель сохраняется в:

```text
experiments/best_model/model.joblib
```

Метрики сохраняются в:

```text
experiments/best_model/validation_metrics.json
```

Запуск обучения:

```bash
python -m src.train
```

## Текущие метрики модели

На validation-выборке:

```text
accuracy: 0.7931
f1-score: 0.7333
model_name: LogisticRegressionTuned
```

Метрики можно посмотреть через DVC:

```bash
dvc metrics show
```

## DVC pipeline

В проекте используется DVC для описания воспроизводимого ML-пайплайна.

Файл пайплайна:

```text
dvc.yaml
```

Пайплайн состоит из этапов:

```text
preprocess → train
```

Проверить состояние DVC:

```bash
dvc status
```

Запустить воспроизведение пайплайна:

```bash
dvc repro
```

Показать метрики:

```bash
dvc metrics show
```

Примечание: в рамках учебной лабораторной данные и модель остаются в Git, так как датасет небольшой. В промышленном проекте исходные данные и ML-артефакты следует хранить во внешнем приватном DVC remote-хранилище, а в Git помещать только код, конфигурации и DVC-метафайлы.

## API-сервис

API реализован на FastAPI.

Основной файл:

```text
src/app.py
```

Запуск API локально:

```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload
```

После запуска документация доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

### Endpoint `/health`

Метод:

```text
GET /health
```

Проверяет состояние API.

Пример ответа:

```json
{
  "status": "ok",
  "service": "diabetes-prediction-api"
}
```

### Endpoint `/predict`

Метод:

```text
POST /predict
```

Выполняет предсказание наличия диабета.

Пример запроса:

```json
{
  "Pregnancies": 6,
  "Glucose": 148,
  "BloodPressure": 72,
  "SkinThickness": 35,
  "Insulin": 0,
  "BMI": 33.6,
  "DiabetesPedigreeFunction": 0.627,
  "Age": 50
}
```

Пример ответа:

```json
{
  "prediction": 1,
  "probability": 0.8146575280180618,
  "label": "detected"
}
```

## Тестирование

Проект покрыт тестами с использованием pytest.

Тестируются:

* API endpoints;
* модуль предсказания;
* preprocessing pipeline;
* training pipeline.

Запуск всех тестов:

```bash
python -m pytest tests -v
```

Ожидаемый результат:

```text
20 passed
```

## Docker

Проект контейнеризован с помощью Docker.

Сборка и запуск через Docker Compose:

```bash
docker compose up --build
```

После запуска API доступно по адресу:

```text
http://127.0.0.1:8000/docs
```

Остановка контейнера:

```bash
docker compose down
```

## DockerHub

Docker image публикуется в DockerHub:

```text
qekqq/mloops_api
```

Pull последней версии образа:

```bash
docker pull qekqq/mloops_api:latest
```

Запуск контейнера из DockerHub image:

```bash
docker run -d --name mloops-api -p 8000:8000 qekqq/mloops_api:latest
```

После запуска API доступно по адресу:

```text
http://127.0.0.1:8000/docs
```

Остановка и удаление контейнера:

```bash
docker rm -f mloops-api
```

## CI/CD

CI/CD реализован с помощью GitHub Actions.

Workflow-файлы:

```text
.github/workflows/ci.yml
.github/workflows/cd.yml
```

### CI pipeline

CI запускается при push / pull request в ветки `develop` и `main`.

CI выполняет:

1. checkout репозитория;
2. установку Python 3.11;
3. установку зависимостей;
4. запуск pytest-тестов;
5. сборку Docker image;
6. push Docker image в DockerHub.

Docker image публикуется с двумя тегами:

```text
latest
<commit_sha>
```

### CD pipeline

CD pipeline запускается после успешного CI, а также может запускаться для ветки `develop`.

CD выполняет:

1. авторизацию в DockerHub;
2. pull Docker image;
3. запуск Docker container;
4. ожидание старта API;
5. функциональный тест `GET /health`;
6. функциональный тест `POST /predict`;
7. вывод логов контейнера;
8. остановку и удаление контейнера.

Функциональные тесты выполняются внутри запущенного контейнера.

## Конфигурация

Основные параметры проекта вынесены в:

```text
config.ini
```

В конфигурации указываются:

* пути к данным;
* параметры разбиения выборки;
* целевая колонка;
* признаки, где нулевые значения считаются пропусками;
* гиперпараметры модели.

## Быстрый запуск проекта

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить preprocessing:

```bash
python -m src.data_preprocessing
```

Обучить модель:

```bash
python -m src.train
```

Запустить тесты:

```bash
python -m pytest tests -v
```

Запустить API:

```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload
```

Запустить через Docker:

```bash
docker compose up --build
```

## Результат

В результате работы был реализован полный учебный MLOps pipeline:

* подготовка данных;
* обучение и сохранение ML-модели;
* API-сервис для инференса;
* тестирование кода;
* DVC pipeline;
* Docker-контейнеризация;
* публикация Docker image в DockerHub;
* CI pipeline для тестов, сборки и публикации image;
* CD pipeline для запуска контейнера и функционального тестирования.
