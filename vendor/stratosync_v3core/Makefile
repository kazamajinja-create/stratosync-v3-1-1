.PHONY: venv install run demo docker-up docker-down

venv:
	python -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8000

demo:
	bash scripts/run_demo.sh

docker-up:
	docker compose up --build

docker-down:
	docker compose down
