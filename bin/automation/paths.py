# -*- coding: utf-8 -*-

"""
Enum important path on the local file systems for this project.

.. note::

    This module is "ZERO-DEPENDENCY".
"""

from pathlib_mate import Path

dir_project_root = Path(__file__).absolute().parent.parent.parent

assert dir_project_root.joinpath("Makefile").exists() is True

dir_python_lib = None
for p in dir_project_root.iterdir():
    if p.joinpath("_version.py").exists():
        dir_python_lib = p

PACKAGE_NAME = dir_python_lib.basename

# ------------------------------------------------------------------------------
# Virtual Environment Related
# ------------------------------------------------------------------------------
dir_venv = dir_project_root / ".venv"
dir_venv_bin = dir_venv / "bin"

# virtualenv executable paths
bin_python = dir_venv_bin / "python"
bin_pip = dir_venv_bin / "pip"
bin_pytest = dir_venv_bin / "pytest"

# ------------------------------------------------------------------------------
# Test Related
# ------------------------------------------------------------------------------
dir_tests = dir_project_root / "tests"

dir_htmlcov = dir_project_root / "htmlcov"

# ------------------------------------------------------------------------------
# Poetry Related
# ------------------------------------------------------------------------------
path_requirements_main = dir_project_root / "requirements-main.txt"
path_requirements_dev = dir_project_root / "requirements-dev.txt"
path_requirements_test = dir_project_root / "requirements-test.txt"
path_requirements_doc = dir_project_root / "requirements-doc.txt"
path_requirements_automation = dir_project_root / "requirements-automation.txt"

path_poetry_lock = dir_project_root / "poetry.lock"
path_poetry_lock_hash_json = dir_project_root / ".poetry-lock-hash.json"

# ------------------------------------------------------------------------------
# Env Related
# ------------------------------------------------------------------------------
path_current_env_name_json = dir_project_root / ".current-env-name.json"

# ------------------------------------------------------------------------------
# Build Related
# ------------------------------------------------------------------------------
dir_build = dir_project_root / "build"
dir_dist = dir_project_root / "dist"

# ------------------------------------------------------------------------------
# Alfred Related
# ------------------------------------------------------------------------------
path_git_repo_info_plist = dir_project_root / "info.plist"
path_git_repo_main_py = dir_project_root / "main.py"
