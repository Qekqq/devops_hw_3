# DevOps HW 2 — Diabetes Prediction API with PostgreSQL

## 1. Описание проекта

Проект реализован в рамках лабораторной работы №2 по курсу DevOps.

Тема лабораторной работы: **«Взаимодействие с источниками данных»**.

Цель работы — реализовать взаимодействие сервиса машинного обучения с базой данных, обеспечить отсутствие явно прописанных секретов в исходном коде, переиспользовать CI/CD pipeline и проверить работу приложения через Docker Compose.

В качестве источника данных по варианту используется **PostgreSQL**.

Проект представляет собой API-сервис для предсказания риска диабета на основе медицинских признаков пациента. Модель машинного обучения обёрнута в FastAPI-сервис, контейнеризована через Docker и запускается совместно с PostgreSQL через Docker Compose.

## 2. Ссылки

GitHub repository:

```text
https://github.com/Qekqq/devops_hw_2
```

DockerHub image:

```text
https://hub.docker.com/repository/docker/qekqq/devops_hw_2_api/general
```

Docker image name:

```text
qekqq/devops_hw_2_api
```

## 3. Основная функциональность

В проекте реализовано:

* FastAPI-сервис для инференса ML-модели;
* PostgreSQL-база данных для хранения данных проекта;
* схема БД с таблицами для пользователей, пациентов, датасетов, моделей и истории прогнозов;
* сохранение результатов работы модели в таблицу `prediction_history`;
* загрузка обработанных train/valid/test данных в таблицы `datasets` и `dataset_samples`;
* хранение параметров подключения к БД через переменные окружения;
* Docker Compose для запуска API и PostgreSQL;
* CI pipeline для тестирования, сборки и публикации Docker image;
* CD pipeline для запуска контейнеров и функционального тестирования;
* автоматизированные тесты через pytest.

## 4. Стек технологий

В проекте использовались:

* Python 3.11;
* FastAPI;
* Uvicorn;
* Pydantic;
* pandas;
* numpy;
* scikit-learn;
* SQLAlchemy;
* psycopg2-binary;
* PostgreSQL 16;
* Docker;
* Docker Compose;
* pytest;
* GitHub Actions;
* DockerHub.

## 5. Структура проекта

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
├── db/
│   ├── 01_schema.sql
│   └── 02_seed.sql
├── experiments/
│   └── best_model/
│       ├── model.joblib
│       └── validation_metrics.json
├── src/
│   ├── db/
│   │   ├── database.py
│   │   ├── load_dataset.py
│   │   ├── models.py
│   │   └── repositories.py
│   ├── app.py
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── features.py
│   ├── logger.py
│   ├── predict.py
│   ├── schemas.py
│   └── train.py
├── tests/
│   ├── test_api.py
│   ├── test_data_preprocessing.py
│   ├── test_predict.py
│   └── test_train.py
├── .dockerignore
├── .gitignore
├── config.ini
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## 6. Конфигурация проекта

Основная конфигурация проекта находится в файле `config.ini`.

В рамках лабораторной работы №2 признаки и метрики были приведены к единому формату именования.

Используемые признаки:

```text
pregnancies
glucose
blood_pressure
skin_thickness
insulin
bmi
diabetes_pedigree_function
age
```

Целевая переменная:

```text
outcome
```

Используемые метрики:

```text
accuracy_score
precision_score
recall_score
f1_score
```

## 7. Переменные окружения

Параметры подключения к PostgreSQL не хранятся в исходном коде. Они передаются через переменные окружения.

Для локального запуска необходимо создать файл `.env` в корне проекта.

Пример `.env`:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=diabetes
POSTGRES_USER=diabetes_owner
POSTGRES_PASSWORD=your_local_password
```

Файл `.env` не должен попадать в Git.

В GitHub Actions аналогичные значения хранятся в Repository Secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

## 8. База данных PostgreSQL

В проекте используется PostgreSQL 16.

Схема БД создаётся автоматически при первом запуске контейнера PostgreSQL через SQL-скрипты из директории `db/`.

Файлы инициализации:

```text
db/01_schema.sql
db/02_seed.sql
```

Основные таблицы:

```text
users
patients
datasets
dataset_samples
model_versions
prediction_history
prediction_feedback
```

Таблица `model_versions` хранит сведения о версии модели, метриках и роли модели. В рамках проекта seed-скрипт добавляет champion-модель:

```text
LogisticRegressionTuned
```

Таблица `prediction_history` хранит результаты вызова `/predict`.

Таблица `dataset_samples` хранит подготовленные train/valid/test строки датасета.

## 9. Запуск через Docker Compose

Для запуска приложения и базы данных используется Docker Compose.

Команда запуска:

```powershell
docker compose up -d --build
```

Проверить состояние контейнеров:

```powershell
docker compose ps
```

Остановить контейнеры:

```powershell
docker compose down
```

Остановить контейнеры и удалить volume PostgreSQL:

```powershell
docker compose down -v
```

## 10. API endpoints

### GET `/health`

Проверяет состояние API-сервиса.

Пример запроса:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Пример ответа:

```json
{
  "status": "ok",
  "service": "diabetes-prediction-api"
}
```

### GET `/db/health`

Проверяет подключение API к PostgreSQL.

Пример запроса:

```powershell
Invoke-RestMethod http://localhost:8000/db/health
```

Пример ответа:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### POST `/predict`

Выполняет прогноз риска диабета и сохраняет результат в PostgreSQL.

Пример входных данных:

```json
{
  "patient_code": "PAT-001",
  "pregnancies": 6,
  "glucose": 148,
  "blood_pressure": 72,
  "skin_thickness": 35,
  "insulin": 0,
  "bmi": 33.6,
  "diabetes_pedigree_function": 0.627,
  "age": 50
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

После успешного вызова `/predict` запись сохраняется в таблицу `prediction_history`.

## 11. Проверка записи прогноза в БД

Подключиться к PostgreSQL:

```powershell
docker exec -it devops_hw_2_db psql -U diabetes_owner -d diabetes
```

Проверить последние прогнозы:

```sql
SELECT
    id,
    patient_code_snapshot,
    prediction,
    probability,
    label,
    request_source,
    response_time_ms,
    created_at
FROM prediction_history
ORDER BY created_at DESC
LIMIT 5;
```

Пример результата:

```text
id | patient_code_snapshot | prediction | probability | label    | request_source | response_time_ms
1  | PAT-001               | 1          | 0.81466     | detected | api            | 12
```

## 12. Загрузка датасета в PostgreSQL

Для загрузки подготовленных train/valid/test данных используется скрипт:

```text
src/db/load_dataset.py
```

Скрипт загружает данные из:

```text
data/processed/train.csv
data/processed/valid.csv
data/processed/test.csv
```

Команда запуска внутри API-контейнера:

```powershell
docker compose exec diabetes-api python -m src.db.load_dataset
```

Проверка таблицы `datasets`:

```sql
SELECT id, dataset_name, dataset_version, source_path, created_at
FROM datasets;
```

Проверка количества строк по split:

```sql
SELECT split, COUNT(*) AS rows_count
FROM dataset_samples
GROUP BY split
ORDER BY split;
```

Ожидаемый результат:

```text
train | 536
valid | 116
test  | 116
```

Суммарно:

```text
768 rows
```

## 13. Локальный запуск тестов

Запуск всех тестов:

```powershell
pytest
```

Ожидаемый результат:

```text
20 passed
```

Тестами покрыты:

```text
tests/test_api.py
tests/test_data_preprocessing.py
tests/test_predict.py
tests/test_train.py
```

## 14. CI pipeline

CI pipeline описан в файле:

```text
.github/workflows/ci.yml
```

CI запускается при:

```text
pull_request в main
push в develop
push в main
workflow_dispatch
```

CI pipeline выполняет:

1. Checkout repository.
2. Установку Python 3.11.
3. Установку зависимостей из `requirements.txt`.
4. Запуск unit-тестов через pytest.
5. Сборку Docker image.
6. Публикацию Docker image в DockerHub.

Используемый Docker image:

```text
qekqq/devops_hw_2_api
```

Теги:

```text
latest
commit_sha
```

## 15. CD pipeline

CD pipeline описан в файле:

```text
.github/workflows/cd.yml
```

CD запускается после успешного CI pipeline через `workflow_run`, а также может быть запущен вручную через `workflow_dispatch`.

CD pipeline выполняет:

1. Checkout repository.
2. Авторизацию в DockerHub.
3. Проверку обязательных GitHub Secrets.
4. Pull Docker image из DockerHub.
5. Создание `.env` файла на runner.
6. Создание временного `docker-compose.cd.yml`.
7. Запуск FastAPI и PostgreSQL через Docker Compose.
8. Проверку `/health`.
9. Проверку `/db/health`.
10. Функциональный тест `/predict`.
11. Загрузку processed-датасета в PostgreSQL.
12. Проверку записей в `prediction_history`.
13. Проверку записей в `dataset_samples`.
14. Вывод статуса сервисов и логов.
15. Остановку контейнеров.

Таким образом, CD pipeline проверяет не только API, но и полноценную интеграцию сервиса модели с PostgreSQL.

## 16. Безопасность конфигурации

В исходном коде отсутствуют явно прописанные пары логин/пароль, адрес/порт сервера базы данных и токены доступа.

Параметры подключения к БД передаются через:

```text
.env
GitHub Repository Secrets
environment variables
```

Файл `src/db/database.py` получает значения из переменных окружения:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Это позволяет запускать один и тот же код в локальной среде и в GitHub Actions без хранения секретов в репозитории.

## 17. DockerHub

Docker image публикуется в DockerHub:

```text
qekqq/devops_hw_2_api
```

Команда pull:

```powershell
docker pull qekqq/devops_hw_2_api:latest
```

## 18. Результаты работы

В результате лабораторной работы №2 было реализовано:

* взаимодействие FastAPI ML-сервиса с PostgreSQL;
* сохранение результата работы модели в БД;
* хранение подготовленных train/valid/test данных в БД;
* отсутствие хардкода секретов в исходном коде;
* запуск API и PostgreSQL через Docker Compose;
* CI pipeline для тестирования, сборки и публикации Docker image;
* CD pipeline для функционального тестирования API и БД;
* публикация Docker image в отдельный DockerHub-репозиторий лабораторной работы №2.

## 19. Вывод

В ходе лабораторной работы был расширен ML-сервис Diabetes Prediction API: к приложению была подключена PostgreSQL-база данных, реализовано сохранение результатов инференса модели и загрузка подготовленных датасетов.

Сервис модели взаимодействует с базой данных через SQLAlchemy, параметры подключения передаются через переменные окружения и GitHub Secrets. Приложение запускается через Docker Compose, что обеспечивает воспроизводимость инфраструктуры.

CI/CD pipeline подтверждает корректность проекта: unit-тесты проходят успешно, Docker image публикуется в DockerHub, а CD pipeline запускает API и PostgreSQL, выполняет функциональные проверки `/health`, `/db/health`, `/predict`, а также проверяет наличие записей в таблицах `prediction_history` и `dataset_samples`.

