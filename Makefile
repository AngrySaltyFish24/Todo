.PHONY: clean clean-build clean-pyc clean-test coverage help lint lint/black
.DEFAULT_GOAL := help
PYTHON=python3

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

VERSION := 0.1.0
PACKAGE_NAME := todo
PACKAGE_FILE := dist/$(PACKAGE_NAME)-$(VERSION).tar.gz

help:
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all test, coverage and Python artifacts

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/

lint/black: ## check style with black
	black todo tests

lint/isort: ## lint with isort
	isort todo tests

lint: lint/black lint/isort ## check style

test: ## run tests quickly with the default Python
	$(PYTHON) -m pytest --verbose tests

typecheck: ## run type checker
	mypy todo \
		--config-file mypy.ini \
		--explicit-package-bases \
		--strict
	$(PYTHON) -m pytest --verbose --mypy-config-file=mypy.ini tests


coverage: ## check code coverage quickly with the default Python
	coverage run -m pytest tests
	coverage report -m
	coverage html

dist: $(PACKAGE_FILE) ## builds source and wheel package

install: $(PACKAGE_FILE) ## install the package to the active Python's site-packages
	$(PYTHON) -m pip install $(PACKAGE_FILE)

$(PACKAGE_FILE): clean 
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build
	@echo "package build in $@"

