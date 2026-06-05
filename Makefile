PYTHON = python
PIP = pip
APP = src.app:app

.PHONY: install preprocess train test run-api run-api-dev

install:
	$(PIP) install -r requirements.txt

preprocess:
	$(PYTHON) -m src.data_preprocessing

train:
	$(PYTHON) -m src.train

test:
	$(PYTHON) -m pytest tests -v

run-api:
	uvicorn $(APP) --host 0.0.0.0 --port 8000

run-api-dev:
	uvicorn $(APP) --host 127.0.0.1 --port 8000 --reload