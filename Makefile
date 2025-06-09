.PHONY: setup

setup: create_venv install_requirements

create_venv:
	@echo "Installing python 3.12"
	uv python install 3.12
	@echo "Creating virtual environment using uv..."
	uv venv .venv
	@echo "Virtual environment created at .venv"

install_requirements:
	@echo "Installing requirements..."
	uv sync

run_app:
	@echo "Starting DroneAgent..."
	python app.py