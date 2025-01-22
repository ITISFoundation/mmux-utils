SHELL := /bin/bash

# Directory for virtual environment
VENV_DIR := ".pyenv"

# Clean target
.PHONY: clean
clean:
	@rm -rf $(VENV_DIR)
	
# Virtual environment target
.PHONY: pyenv
pyenv: clean
	@python -m venv $(VENV_DIR)
	@. ./$(VENV_DIR)/bin/activate && pip install wheel && pip install .

.PHONY: test_make_wheel
test_make_wheel: pyenv
	@pip install wheel
	@python setup.py bdist_wheel

# .PHONY: test_mmux_utils_install
# test_mmux_utils_install: pyenv
# 	@python -m pip show mmux_utils