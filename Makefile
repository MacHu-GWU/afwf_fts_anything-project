# -*- coding: utf-8 -*-

help: ## ** Show this help message
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


venv-create: ## ** Create Virtual Environment
	python ./bin/s01_1_virtualenv_venv_create.py


venv-remove: ## ** Remove Virtual Environment
	python ./bin/s01_2_venv_remove.py


install: ## ** Install main dependencies and Package itself
	python ./bin/s02_1_pip_install.py


install-dev: ## Install Development Dependencies
	python ./bin/s02_2_pip_install_dev.py


install-test: ## Install Test Dependencies
	python ./bin/s02_3_pip_install_test.py


install-doc: ## Install Document Dependencies
	python ./bin/s02_4_pip_install_doc.py


install-all: ## Install All Dependencies
	python ./bin/s02_5_pip_install_all.py


poetry-export: ## Export requirements-*.txt from poetry.lock file
	python ./bin/s02_6_poetry_export.py


poetry-lock: ## Resolve dependencies using poetry, update poetry.lock file
	python ./bin/s02_7_poetry_lock.py


test: install install-test test-only ## ** Run test


test-only: ## Run test without checking test dependencies
	./.venv/bin/python ./bin/s03_1_run_unit_test.py


cov: install install-test cov-only ## ** Run code coverage test


cov-only: ## Run code coverage test without checking test dependencies
	./.venv/bin/python ./bin/s03_2_run_cov_test.py


build-wf: ## ** Build Alfred Workflow release from source code
	python ./bin/s05_1_build_wf.py


refresh-code: ## ** Refresh Alfred Workflow source code
	python ./bin/s05_2_refresh_code.py
