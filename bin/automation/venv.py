# -*- coding: utf-8 -*-

"""
Virtualenv management.

.. note::

    This module is "ZERO-DEPENDENCY".
"""

import subprocess

from .paths import dir_venv
from .config import config
from .logger import logger


@logger.pretty_log(
    start_msg="Create 🐍 Virtual Environment",
    end_msg="End 'Create Virtual Environment', elapsed = {elapsed} sec",
)
def poetry_venv_create():
    """
    .. code-block:: bash

        $ poetry config virtualenvs.in-project true --local
        $ poetry env use python${X}.${Y}
    """
    if not dir_venv.exists():
        subprocess.run(
            ["poetry", "config", "virtualenvs.in-project", "true", "--local"],
            check=True,
        )
        subprocess.run(
            ["poetry", "env", "use", f"python{config.python_version}"],
            check=True,
        )
        logger.info("done")
    else:
        logger(f"{dir_venv} already exists, do nothing.")


@logger.pretty_log(
    start_msg="Create 🐍 Virtual Environment",
    end_msg="End 'Create Virtual Environment', elapsed = {elapsed} sec",
)
def virtualenv_venv_create():
    """
    .. code-block:: bash

        $ virtualenv -p python${X}.${Y} ./.venv
    """
    if not dir_venv.exists():
        subprocess.run(
            ["virtualenv", "-p", f"python{config.python_version}", f"{dir_venv}"],
            check=True,
        )
        logger.info("done")
    else:
        logger.info(f"{dir_venv} already exists, do nothing.")


@logger.pretty_log(
    start_msg="Remove 🐍 Virtual Environment",
    end_msg="End 'Remove Virtual Environment', elapsed = {elapsed} sec",
)
def venv_remove():
    """
    .. code-block:: bash

        $ rm -r ./.venv
    """
    if dir_venv.exists():
        subprocess.run(["rm", "-r", f"{dir_venv}"])
        logger.info(f"done! {dir_venv} is removed.")
    else:
        logger.info(f"{dir_venv} doesn't exists, do nothing.")
