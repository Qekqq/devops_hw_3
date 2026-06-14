# DevOps HW 3 — Diabetes Prediction API with Hashicorp Vault

## 1. Описание проекта

Проект выполнен в рамках лабораторной работы №3 по дисциплине «Инфраструктура больших данных».

Тема лабораторной работы: **«Размещение секретов в хранилище»**.

Цель работы — реализовать хранение секретов в специализированном хранилище и настроить взаимодействие сервиса машинного обучения с этим хранилищем.

В качестве хранилища секретов используется **Hashicorp Vault**.

Проект основан на лабораторной работе №2. В предыдущей версии был реализован FastAPI-сервис машинного обучения, PostgreSQL-база данных, сохранение результатов прогнозирования и CI/CD pipeline. В лабораторной работе №3 проект был расширен: параметры подключения к PostgreSQL теперь размещаются в Vault, а API-сервис получает их из Vault при обращении к базе данных.

## 2. Ссылки

GitHub repository:

```text
https://github.com/Qekqq/devops_hw_3
```

DockerHub image:

```text
https://hub.docker.com/repository/docker/qekqq/devops_hw_3_api/general
```

Docker image name:

```text
qekqq/devops_hw_3_api
```

## 3. Основная функциональность

В проекте реализовано:

* FastAPI API-сервис для инференса ML-модели;
* PostgreSQL-база данных для хранения данных проекта;
* Hashicorp Vault для хранения секретов подключения к БД;
* init-контейнер `vault-init` для записи секретов PostgreSQL в Vault;
* получение параметров подключения к PostgreSQL через Vault;
* сохранение результата работы модели в таблицу `prediction_history`;
* загрузка обработанного датасета в таблицы `datasets` и `dataset_samples`;
* Docker Compose для запуска API, PostgreSQL, Vault и vault-init;
* CI pipeline для тестирования, сборки Docker image и публикации в DockerHub;
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
* hvac;
* PostgreSQL 16;
* Hashicorp Vault;
* Docker;
* Docker Compose;
* pytest;
* GitHub Actions;
* DockerHub.

## 5. Архитектура проекта

Архитектура лабораторной работы №3:

```text
GitHub Secrets / local .env
        ↓
vault-init
        ↓
Hashicorp Vault
        ↓
FastAPI service
        ↓
PostgreSQL
```

Логика работы:

1. PostgreSQL запускается как отдельный контейнер.
2. Vault запускается как отдельный контейнер в dev-режиме.
3. Контейнер `vault-init` получает параметры PostgreSQL из переменных окружения и записывает их в Vault.
4. FastAPI-сервис при обращении к БД читает параметры подключения из Vault.
5. После этого API подключается к PostgreSQL и сохраняет результат работы модели.

## 6. Структура проекта

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
│   ├── secrets/
│   │   ├── __init__.py
│   │   └── vault_client.py
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
├── vault/
│   └── init-vault.sh
├── .dockerignore
├── .env.example
├── .gitignore
├── config.ini
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## 7. Конфигурация окружения

В проекте используется `.env.example` как шаблон локальной конфигурации.

Пример `.env.example`:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=diabetes
POSTGRES_USER=diabetes_owner
POSTGRES_PASSWORD=change_me

VAULT_ADDR=http://vault:8200
VAULT_TOKEN=change_me
VAULT_KV_MOUNT=secret
VAULT_DB_SECRET_PATH=database/postgres
```

Файл `.env` создаётся локально и не должен попадать в Git.

В GitHub Actions значения передаются через Repository Secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
VAULT_TOKEN
```

## 8. Hashicorp Vault

В лабораторной работе №3 добавлен сервис Hashicorp Vault.

Vault запускается в `docker-compose.yml` как отдельный контейнер:

```text
devops_hw_3_vault
```

Для инициализации Vault используется отдельный контейнер:

```text
devops_hw_3_vault_init
```

Он выполняет скрипт:

```text
vault/init-vault.sh
```

Скрипт записывает параметры подключения к PostgreSQL в Vault по пути:

```text
secret/data/database/postgres
```

В Vault записываются следующие параметры:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

После успешной записи секретов init-контейнер завершает работу со статусом `Exited (0)`.

## 9. Получение секретов в приложении

Для взаимодействия с Vault реализован файл:

```text
src/secrets/vault_client.py
```

Он использует библиотеку `hvac` и читает секреты из Vault.

Файл:

```text
src/db/database.py
```

был обновлён. Теперь он не читает параметры PostgreSQL напрямую из `.env`, а получает их через функцию:

```text
get_database_secrets()
```

После получения секретов формируется SQLAlchemy connection URL, создаётся engine и открывается сессия для работы с PostgreSQL.

Таким образом, исходный код не содержит логин, пароль, адрес, порт базы данных или токены доступа.

## 10. Запуск проекта через Docker Compose

Запуск контейнеров:

```powershell
docker compose up -d --build
```

Проверка контейнеров:

```powershell
docker compose ps
```

Ожидаемые сервисы:

```text
devops_hw_3_api
devops_hw_3_db
devops_hw_3_vault
devops_hw_3_vault_init
```

Контейнер `devops_hw_3_vault_init` после выполнения может быть завершён со статусом `Exited (0)`. Это нормальное поведение, так как он нужен только для записи секретов в Vault.

Остановка контейнеров:

```powershell
docker compose down
```

Остановка контейнеров с удалением volume PostgreSQL:

```powershell
docker compose down -v
```

## 11. Проверка Vault init

Посмотреть логи init-контейнера:

```powershell
docker compose logs vault-init
```

Ожидаемый результат:

```text
Waiting for Vault...
Vault is available
Writing PostgreSQL secrets to Vault...
PostgreSQL secrets were written to Vault
```

Эти логи подтверждают, что параметры PostgreSQL были записаны в Hashicorp Vault.

## 12. API endpoints

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

В ЛР3 этот endpoint подтверждает, что сервис смог получить параметры подключения к БД из Vault и подключиться к PostgreSQL.

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
  "patient_code": "LAB3-PAT-001",
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

После выполнения запроса результат сохраняется в таблицу `prediction_history`.

## 13. Проверка записи прогноза в PostgreSQL

Подключение к PostgreSQL:

```powershell
docker exec -it devops_hw_3_db psql -U diabetes_owner -d diabetes
```

SQL-запрос:

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
1  | LAB3-PAT-001          | 1          | 0.81466     | detected | api            | 21
```

## 14. Загрузка датасета в PostgreSQL

Для загрузки подготовленного датасета используется скрипт:

```text
src/db/load_dataset.py
```

Команда запуска:

```powershell
docker compose exec diabetes-api python -m src.db.load_dataset
```

Проверка количества строк:

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

## 15. Локальные тесты

Запуск тестов:

```powershell
pytest
```

Ожидаемый результат:

```text
20 passed
```

Проверяется:

```text
tests/test_api.py
tests/test_data_preprocessing.py
tests/test_predict.py
tests/test_train.py
```

## 16. CI pipeline

CI pipeline описан в файле:

```text
.github/workflows/ci.yml
```

CI выполняет:

1. Checkout repository.
2. Установку Python 3.11.
3. Установку зависимостей из `requirements.txt`.
4. Запуск unit-тестов через pytest.
5. Сборку Docker image.
6. Публикацию Docker image в DockerHub.

Docker image:

```text
qekqq/devops_hw_3_api
```

Теги:

```text
latest
commit_sha
```

## 17. CD pipeline

CD pipeline описан в файле:

```text
.github/workflows/cd.yml
```

CD pipeline выполняет:

1. Checkout repository.
2. Авторизацию в DockerHub.
3. Проверку обязательных GitHub Secrets.
4. Pull Docker image из DockerHub.
5. Создание `.env` файла на runner.
6. Создание временного `docker-compose.cd.yml`.
7. Запуск API, PostgreSQL, Vault и vault-init.
8. Вывод логов `vault-init`.
9. Проверку `/health`.
10. Проверку `/db/health`.
11. Функциональный тест `/predict`.
12. Загрузку processed-датасета в PostgreSQL.
13. Проверку записей в `prediction_history`.
14. Проверку записей в `dataset_samples`.
15. Вывод логов API и Vault.
16. Остановку контейнеров.

CD pipeline подтверждает, что сервис работает в контейнерной инфраструктуре и получает параметры подключения к PostgreSQL из Hashicorp Vault.

## 18. DockerHub

Docker image публикуется в DockerHub:

```text
qekqq/devops_hw_3_api
```

Команда pull:

```powershell
docker pull qekqq/devops_hw_3_api:latest
```

## 19. Безопасность

В исходном коде отсутствуют явно прописанные:

```text
логин БД
пароль БД
адрес БД
порт БД
токены доступа
```

Секреты передаются через переменные окружения и записываются в Hashicorp Vault. API-сервис получает параметры подключения к PostgreSQL из Vault при создании подключения к базе данных.

Файл `.env` используется только локально и не добавляется в Git. В GitHub Actions секреты хранятся в Repository Secrets.

## 20. Результаты работы

В результате лабораторной работы №3 было реализовано:

* подключение Hashicorp Vault к проекту;
* размещение параметров PostgreSQL в Vault;
* init-контейнер для записи секретов в Vault;
* Python-клиент для чтения секретов из Vault;
* получение параметров подключения к БД из Vault;
* сохранение защищённого обращения API к PostgreSQL;
* запуск API, PostgreSQL и Vault через Docker Compose;
* CI/CD pipeline для сборки, публикации Docker image и функционального тестирования;
* публикация Docker image в отдельный DockerHub-репозиторий ЛР3.

## 21. Вывод

В ходе лабораторной работы №3 ML-сервис Diabetes Prediction API был расширен интеграцией с Hashicorp Vault. Теперь параметры подключения к PostgreSQL не хранятся в исходном коде и не передаются напрямую в приложение как основная конфигурация подключения. Вместо этого они записываются в Vault и считываются API-сервисом при обращении к базе данных.

Система запускается через Docker Compose и включает FastAPI API, PostgreSQL, Hashicorp Vault и init-контейнер для записи секретов. CI/CD pipeline подтверждает корректность проекта: тесты проходят успешно, Docker image публикуется в DockerHub, а CD pipeline запускает контейнеры и проверяет `/health`, `/db/health`, `/predict`, запись прогнозов в БД и загрузку датасета.


