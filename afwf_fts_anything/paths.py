# -*- coding: utf-8 -*-

from pathlib_mate import Path

dir_python_lib = Path.dir_here(__file__)
dir_project_root = dir_python_lib.parent

PACKAGE_NAME = dir_python_lib.basename

# ------------------------------------------------------------------------------
# Alfred Related
# ------------------------------------------------------------------------------
dir_home = Path.home()
dir_project_home = dir_home / ".alfred-afwf" / PACKAGE_NAME
dir_project_home.mkdir_if_not_exists()

dir_cache = dir_project_home / ".cache"
path_settings_sqlite = dir_project_home / "settings.sqlite"

path_config_json = dir_project_home / "config.json"

# ------------------------------------------------------------------------------
# Virtual Environment Related
# ------------------------------------------------------------------------------
dir_venv = dir_project_root / ".venv"
dir_venv_bin = dir_venv / "bin"

# virtualenv executable paths
bin_pytest = dir_venv_bin / "pytest"

# test related
dir_htmlcov = dir_project_root / "htmlcov"
path_cov_index_html = dir_htmlcov / "index.html"
dir_unit_test = dir_project_root / "tests"
dir_int_test = dir_project_root / "tests_int"
