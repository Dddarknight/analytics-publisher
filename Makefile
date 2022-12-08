lint:
	poetry run flake8 .

install:
	poetry install

run:
	poetry run uvicorn api_app.server:app --reload

bot:
	poetry run python bot/bot.py