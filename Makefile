.PHONY: install test lint validate migrate seed up down

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	flake8 .

validate:
	python scripts/validate_repository.py
	python scripts/validate_schemas.py

migrate:
	alembic upgrade head

seed:
	python scripts/seed_registry.py

up:
	docker compose up --build

down:
	docker compose down
