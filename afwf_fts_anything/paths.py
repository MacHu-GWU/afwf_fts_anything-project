# -*- coding: utf-8 -*-

from pathlib import Path
from functools import cached_property

_dir_here = Path(__file__).absolute().parent
PACKAGE_NAME = _dir_here.name


class PathEnum:
    """
    Centralized enumeration of all project paths with absolute path references.

    Provides IDE-autocomplete-friendly access to all project directories and files using
    absolute paths to eliminate current directory dependencies and ensure consistent path
    resolution across different execution contexts and DevOps workflows.
    """

    @cached_property
    def dir_home(self):
        return Path.home()

    dir_project_root = _dir_here.parent
    dir_tmp = dir_project_root / "tmp"

    # Source Code
    dir_package = _dir_here
    path_version_py = dir_package / "_version.py"
    path_pyproject_toml = dir_project_root / "pyproject.toml"
    path_requirements_txt = dir_project_root / "requirements.txt"
    path_authors = dir_project_root / "AUTHORS.txt"
    path_license = dir_project_root / "LICENSE.txt"
    path_release_history = dir_project_root / "release-history.rst"

    # Virtual Environment
    dir_venv = dir_project_root / ".venv"
    dir_venv_bin = dir_venv / "bin"
    path_venv_bin_pip = dir_venv_bin / "pip"
    path_venv_bin_python = dir_venv_bin / "python"
    path_venv_bin_pytest = dir_venv_bin / "pytest"

    # Test
    dir_htmlcov = dir_project_root / "htmlcov"
    path_cov_index_html = dir_htmlcov / "index.html"
    dir_unit_test = dir_project_root / "tests"
    dir_int_test = dir_project_root / "tests_int"
    dir_load_test = dir_project_root / "tests_load"

    path_setting = dir_unit_test / "movie-setting.json"
    path_data = dir_unit_test / "movie-data.json"
    dir_index = dir_unit_test / "movie-whoosh_index"
    dir_icon = dir_unit_test / "movie-icon"

    # Documentation
    dir_docs_source = dir_project_root / "docs" / "source"
    dir_docs_build_html = dir_project_root / "docs" / "build" / "html"

    # Build
    dir_build = dir_project_root / "build"
    dir_dist = dir_project_root / "dist"

    @cached_property
    def dir_project_home(self):
        return self.dir_home / ".alfred-afwf" / PACKAGE_NAME

    @cached_property
    def dir_cache(self):
        return self.dir_project_home / ".cache"


path_enum = PathEnum()
"""
Single entry point for all project paths with absolute path references.
"""
