# Makefile
.PHONY: setup install run clean docker-up docker-down test lint conda-clean conda-init docker-setup

setup: clean conda-init install docker-setup docker-up
	@echo "Setup complete!"

docker-setup:
	@if [ ! -f docker-compose.override.yml ] && [ -f docker-compose.override.yml.example ]; then \
		echo "Creating docker-compose.override.yml..."; \
		cp docker-compose.override.yml.example docker-compose.override.yml; \
	fi

conda-init:
	@if command -v conda >/dev/null 2>&1; then \
		conda init zsh || true; \
		conda init bash || true; \
		echo "Conda initialized."; \
	else \
		echo "Conda not found. Please install Conda first."; \
		exit 1; \
	fi

install:
	@if command -v conda >/dev/null 2>&1; then \
		echo "Creating Conda environment..." && \
		conda env create -f environment.yml || true; \
	else \
		echo "Conda not found, using pip with venv..." && \
		python -m venv mine_venv && \
		. mine_venv/bin/activate && pip install -r requirements.txt; \
	fi

docker-up:
	docker compose -f docker-compose.base.yml -f docker-compose.override.yml up -d

docker-down:
	docker compose -f docker-compose.base.yml -f docker-compose.override.yml down

run:
	@if ! conda info --envs | grep -q mine_venv; then \
		echo "Error: mine_venv environment not activated. Please run: conda activate mine_venv"; \
		exit 1; \
	fi
	python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

clean: docker-down conda-clean
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf mine_venv/
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/

conda-clean:
	@if command -v conda >/dev/null 2>&1; then \
		conda deactivate 2>/dev/null || true; \
		conda env remove -n mine_venv --yes 2>/dev/null || true; \
	fi

lint:
	@if ! conda info --envs | grep -q mine_venv; then \
		echo "Error: mine_venv environment not activated. Please run: conda activate mine_venv"; \
		exit 1; \
	fi
	flake8 .
	black .

test:
	@if ! conda info --envs | grep -q mine_venv; then \
		echo "Error: mine_venv environment not activated. Please run: conda activate mine_venv"; \
		exit 1; \
	fi
	pytest