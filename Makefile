SHELL := /bin/bash
PY := "$(CURDIR)/.venv/bin/python"
BACK := cd backend && $(PY)
.PHONY: setup ingest ingest-offline migrate dev build run test e2e lint verify clean-user
setup:
	python3 -m venv .venv
	$(PY) -m pip install -e ./backend
	cd frontend && npm ci
	$(PY) -c "from pathlib import Path; import shutil; p=Path('.env'); p.exists() or shutil.copy('.env.example',p)"
ingest:
	$(BACK) -m ingest.build_bank --dump-fixtures
ingest-offline:
	$(BACK) -m ingest.build_bank --offline
migrate:
	$(BACK) -m alembic upgrade head
dev:
	$(PY) scripts/dev.py
build:
	cd frontend && npm run build
run: migrate
	$(PY) scripts/serve.py
test:
	$(BACK) -m pytest --cov=app.engine --cov=ingest --cov-report=term-missing --cov-report=json:../data/coverage.json --cov-fail-under=85
	cd frontend && npm test -- --coverage
lint:
	$(BACK) -m ruff check app ingest tests
	$(BACK) -m mypy app ingest
	cd frontend && npm run lint
e2e: build
	$(PY) scripts/e2e.py
verify:
	bash scripts/verify.sh
clean-user:
	$(PY) scripts/clean_user.py
