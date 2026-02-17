.PHONY: dev lint fmt test db-upgrade db-revision db-reset docker-build docker-up docker-down

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .

fmt:
	ruff format .

test:
	pytest -q

db-upgrade:
	alembic upgrade head

db-revision:
	alembic revision --autogenerate -m "$(m)"

db-reset:
	rm -f data/app.db
	alembic upgrade head

docker-build:
	docker build -t ticket-demo:latest .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

