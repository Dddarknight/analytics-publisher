lint:
	poetry run flake8 .

install:
	poetry install

# test-coverage:
# 	poetry run pytest --cov=. --cov-report xml

# test:
# 	poetry run pytest

run:
	poetry run uvicorn api_app.server:app --reload