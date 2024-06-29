REPOSITORY = process-data-flow
SOURCE = process_data_flow


build:
	@docker build -t $(REPOSITORY):latest .

install:
	@echo "\nInstalling project..."
	@poetry install --no-root
	@echo "\nProject installed!"

init_containers:
	@docker compose up -d

check_format:
	@poetry run ruff format $(SOURCE) --check

format:
	@poetry run ruff format $(SOURCE)

check_lint:
	@poetry run ruff check $(SOURCE)

lint:
	@poetry run ruff check $(SOURCE) --fix

check_types:
	@poetry run mypy $(SOURCE)

check_all: check_format check_lint check_types
	@echo "\nAll checks have been passed!"

prepare_env_pyenv:
	@echo "\nPreparing virtualenv using pyenv..."
	@pyenv update
	@pyenv install 3.11.3 -s
	@pyenv virtualenv -f 3.11.3 process_data_flow-env
	@pyenv local process_data_flow-env

	@echo "\nInstalling poetry..."
	@pip install poetry
	@poetry config virtualenvs.create false --local
	@poetry config virtualenvs.prefer-active-python true --local

	@echo "\nProject prepared to install!"

install_with_pyenv: prepare_env_pyenv install
	@echo "\nProject installed with pyenv!"