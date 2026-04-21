# -*- coding: utf-8 -*-

"""
Print PyPI URL after publish.
"""

from utils import config

project_name = config.project_name
version = config.pyproject_data["project"]["version"]
pypi_url = f"https://pypi.org/project/{project_name}/{version}/"

print(f"📦 Will publish to PyPI: {pypi_url}")
