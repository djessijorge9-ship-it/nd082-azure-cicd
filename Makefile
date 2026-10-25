PYTHON ?= python

.PHONY: setup install lint test package all run
setup:
	$(PYTHON) -m venv .venv
install:
	$(PYTHON) -m pip install -r requirements-dev.txt
lint:
	$(PYTHON) -m pylint app.py scripts tests
test:
	$(PYTHON) -m pytest -v --junitxml=test-results/junit.xml
package:
	$(PYTHON) scripts/package_app.py
all: install lint test package
run:
	$(PYTHON) -m flask --app app run --host 127.0.0.1 --port 5000
