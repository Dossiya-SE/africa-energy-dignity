.PHONY: install test lint validate migrate seed web-install web-lint web-typecheck web-test web-build up down

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

web-install:
	cd web && npm install

test:
	pytest -q

web-test:
	cd web && npm run test

lint:
	flake8 .

web-lint:
	cd web && npm run lint

web-typecheck:
	cd web && npm run typecheck

web-build:
	cd web && npm run build

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
