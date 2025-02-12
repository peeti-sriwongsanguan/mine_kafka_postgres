# Makefile
.PHONY: setup install run clean docker-up docker-down test lint

setup: install docker-up
	@echo "Setup complete!"

install:
	python -m venv mine_venv
	. venv/bin/activate && pip install -r requirements.txt

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

run:
	. mine_venv/bin/activate && python -m uvicorn app.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf venv/

lint:
	. venv/bin/activate && flake8 .
	. venv/bin/activate && black .

test:
	. venv/bin/activate && pytest