PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff

.PHONY: test lint format check

test:
	$(PYTEST) backend/

lint:
	$(RUFF) check backend/

format:
	$(RUFF) format backend/

check: lint test
