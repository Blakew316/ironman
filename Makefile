.PHONY: help setup install install-all test run web lint clean

VENV ?= .venv
PY   ?= $(VENV)/bin/python
PIP  ?= $(VENV)/bin/pip

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup:  ## Full macOS setup (brew deps + venv + install)
	bash scripts/setup_mac.sh

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)  ## Editable install with core voice + web features
	$(PIP) install -e ".[voice,audio,system,jokes,weather,knowledge,web,config]"

install-all: $(VENV)  ## Editable install with ALL optional features
	$(PIP) install -e ".[all,web,dev]"

test: $(VENV)  ## Run the test suite
	$(PY) -m pytest -q

run:  ## Launch the voice assistant in the terminal
	$(PY) -m jarvis

web:  ## Launch the animated web HUD (http://127.0.0.1:8731)
	$(PY) -m jarvis.web

clean:  ## Remove caches and build artifacts
	rm -rf build dist *.egg-info .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
