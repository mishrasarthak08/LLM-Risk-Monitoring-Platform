.PHONY: install test test-all e2e lint seed-db backend frontend worker audit-verify ci-regression dev

install:
	python3 -m pip install --upgrade pip
	pip install uv
	uv venv --python 3.12 .venv || true
	uv pip install --python .venv/bin/python -r requirements.txt
	cd frontend && npm install

test:
	PYTHONPATH=. .venv/bin/pytest tests/test_*.py -v

e2e:
	cd frontend && npx playwright test

test-all: test e2e

seed-db:
	PYTHONPATH=. .venv/bin/python backend/app/scripts/seed_demo_data.py

backend:
	PYTHONPATH=. .venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	PYTHONPATH=. .venv/bin/celery -A backend.app.worker.celery_app worker --loglevel=info

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting VERITAS AI Backend, Worker & Frontend..."
	@echo "Run 'make backend', 'make worker', and 'make frontend' in separate terminals."

audit-verify:
	PYTHONPATH=. .venv/bin/python ci/veritas_audit.py

ci-regression:
	PYTHONPATH=. .venv/bin/python ci/veritas_ci.py \
		--baseline app/feature/prompts/credit_memo_v1.yaml \
		--candidate app/feature/prompts/credit_memo_v1.yaml \
		--dataset monitoring/golden_set/data/v0001_credit_memo.jsonl
