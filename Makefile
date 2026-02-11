.PHONY: up down load api ui test

up:
	docker compose up -d

down:
	docker compose down -v

load:
	python scripts/load_data.py

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

ui:
	streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

test:
	pytest -q
