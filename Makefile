.PHONY: install test lint migrate seed-db dashboard

install:
	pip install --upgrade pip
	pip install -e .[dev]

test:
	pytest tests/ -v

lint:
	flake8 app monitoring dashboard scripts tests
	mypy app monitoring dashboard scripts tests

migrate:
	alembic upgrade head

seed-db:
	python scripts/seed_mock_data.py

dashboard:
	streamlit run dashboard/streamlit_app/app.py
