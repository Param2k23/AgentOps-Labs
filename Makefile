.PHONY: backend-install backend-lint backend-format backend-typecheck backend-test frontend-install frontend-dev frontend-lint frontend-format frontend-typecheck frontend-build compose-up compose-down

backend-install:
	cd backend && poetry install

backend-lint:
	cd backend && poetry run ruff check .

backend-format:
	cd backend && poetry run black .

backend-typecheck:
	cd backend && poetry run mypy .

backend-test:
	cd backend && poetry run pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-lint:
	cd frontend && npm run lint

frontend-format:
	cd frontend && npm run format

frontend-typecheck:
	cd frontend && npm run typecheck

frontend-build:
	cd frontend && npm run build

compose-up:
	docker compose up --build

compose-down:
	docker compose down
