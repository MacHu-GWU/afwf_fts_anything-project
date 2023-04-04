# -*- coding: utf-8 -*-

"""
Dependencies management
"""

import typing as T
import json
import subprocess
from pathlib_mate import Path

from .paths import (
    dir_project_root,
    bin_pip,
    path_requirements_main,
    path_requirements_dev,
    path_requirements_test,
    path_requirements_doc,
    path_requirements_automation,
    path_poetry_lock,
    path_poetry_lock_hash_json,
)
from .logger import logger
from .helpers import sha256_of_bytes
from .runtime import IS_CI


@logger.pretty_log(
    start_msg="⏱ 💾 Install main dependencies and Package itself",
    end_msg="⏰ End 'Install main dependencies and Package itself', elapsed = {elapsed} sec",
)
def poetry_install():
    """
    ``poetry install``
    """
    subprocess.run(["poetry", "install"], check=True)


@logger.pretty_log(
    start_msg="⏱ 💾 Install dev dependencies",
    end_msg="⏰ End 'Install dev dependencies', elapsed = {elapsed} sec",
)
def poetry_install_dev():
    """
    ``poetry install --with dev``
    """
    subprocess.run(["poetry", "install", "--with", "dev"], check=True)


@logger.pretty_log(
    start_msg="⏱ 💾 Install test dependencies",
    end_msg="⏰ End 'Install test dependencies', elapsed = {elapsed} sec",
)
def poetry_install_test():
    """
    ``poetry install --with test``
    """
    subprocess.run(["poetry", "install", "--with", "test"], check=True)


@logger.pretty_log(
    start_msg="⏱ 💾 Install doc dependencies",
    end_msg="⏰ End 'Install doc dependencies', elapsed = {elapsed} sec",
)
def poetry_install_doc():
    """
    ``poetry install --with doc``
    """
    subprocess.run(["poetry", "install", "--with", "doc"], check=True)


@logger.pretty_log(
    start_msg="⏱ 💾 Install all dependencies for dev, test, doc",
    end_msg="⏰ End 'Install all dependencies for dev, test, doc', elapsed = {elapsed} sec",
)
def poetry_install_all():
    """
    ``poetry install --with dev,test,doc``
    """
    subprocess.run(["poetry", "install", "--with", "dev,test,doc"], check=True)


def do_we_need_poetry_export(poetry_lock_hash: str) -> bool:
    """
    Compare the given poetry.lock file cache to the value stored in the
    ``poetry.lock.hash`` file. If matches, then we don't need to do poetry export.
    Otherwise, we should do poetry export.

    :param poetry_lock_hash: the sha256 hash of the ``poetry.lock`` file
    """
    if path_poetry_lock_hash_json.exists():
        cached_poetry_lock_hash = json.loads(path_poetry_lock_hash_json.read_text())[
            "hash"
        ]
        return poetry_lock_hash != cached_poetry_lock_hash
    else:
        return True


def _poetry_export_group(group: str, path: Path):
    """
    Export dependency group to given path. Usually a requirements.txt file.
    """
    subprocess.run(
        [
            "poetry",
            "export",
            "--format",
            "requirements.txt",
            "--output",
            f"{path}",
            "--only",
            group,
        ],
        check=True,
    )


def _poetry_export(poetry_lock_hash: str):
    path_list = [
        path_requirements_main,
        path_requirements_dev,
        path_requirements_test,
        path_requirements_doc,
    ]
    for path in path_list:
        path.remove_if_exists()

    logger.info(f"export to {path_requirements_main.name}")
    subprocess.run(
        [
            "poetry",
            "export",
            "--format",
            "requirements.txt",
            "--output",
            f"{path_requirements_main}",
        ],
        check=True,
    )

    for group, path in [
        ("dev", path_requirements_dev),
        ("test", path_requirements_test),
        ("doc", path_requirements_doc),
    ]:
        logger.info(f"export to {path.name}")
        _poetry_export_group(group, path)

    path_poetry_lock_hash_json.write_text(
        json.dumps(
            {
                "hash": poetry_lock_hash,
                "description": "DON'T edit this file manually!",
            },
            indent=4,
        )
    )


@logger.pretty_log(
    start_msg="⏱ Export resolved dependency to requirements-***.txt file",
    end_msg="⏰ End 'Export resolved dependency to requirements-***.txt file', elapsed = {elapsed} sec",
)
def poetry_export():
    # calculate the poetry.lock file
    poetry_lock_hash = sha256_of_bytes(path_poetry_lock.read_bytes())
    if do_we_need_poetry_export(poetry_lock_hash) is False:
        logger.info("already did, do nothing")
        return
    _poetry_export(poetry_lock_hash)


def _try_poetry_export():
    """
    Run poetry export when needed.

    This function will be used by other functions to export the dependencies,
    then we can do pip install.
    """
    poetry_lock_hash = sha256_of_bytes(path_poetry_lock.read_bytes())
    if do_we_need_poetry_export(poetry_lock_hash):
        _poetry_export(poetry_lock_hash)


@logger.pretty_log(
    start_msg="⏱ Resolve Dependencies Tree",
    end_msg="⏰ End 'Resolve Dependencies Tree', elapsed = {elapsed} sec",
)
def poetry_lock():
    """
    cmd: ``poetry lock``
    """
    with dir_project_root.temp_cwd():
        subprocess.run(["poetry", "lock"])


def _quite_pip_install_in_ci(args: T.List[str]):
    if IS_CI:
        args.append("--quiet")


@logger.pretty_log(
    start_msg="⏱ 💾 Install main dependencies and Package itself",
    end_msg="⏰ End 'Install main dependencies and Package itself', elapsed = {elapsed} sec",
)
def pip_install():
    """
    cmd: ``pip install -e . --no-deps``
    """
    _try_poetry_export()

    subprocess.run(
        [f"{bin_pip}", "install", "-e", f"{dir_project_root}", "--no-deps"],
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_main}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )


@logger.pretty_log(
    start_msg="⏱ 💾 Install dev dependencies",
    end_msg="⏰ End 'Install dev dependencies', elapsed = {elapsed} sec",
)
def pip_install_dev():
    """
    cmd: ``pip install -r requirements-dev.txt``
    """
    _try_poetry_export()

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_dev}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )


@logger.pretty_log(
    start_msg="⏱ 💾 Install test dependencies",
    end_msg="⏰ End 'Install test dependencies', elapsed = {elapsed} sec",
)
def pip_install_test():
    """
    cmd: ``pip install -r requirements-test.txt``
    """
    _try_poetry_export()

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_test}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )


@logger.pretty_log(
    start_msg="⏱ 💾 Install doc dependencies",
    end_msg="⏰ End 'Install doc dependencies', elapsed = {elapsed} sec",
)
def pip_install_doc():
    """
    cmd: ``pip install -r requirements-doc.txt``
    """
    _try_poetry_export()

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_doc}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )


@logger.pretty_log(
    start_msg="⏱ 💾 Install automation dependencies",
    end_msg="⏰ End 'Install automation dependencies', elapsed = {elapsed} sec",
)
def pip_install_automation():
    """
    cmd: ``pip install -r requirements-automation.txt``
    """
    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_automation}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )


@logger.pretty_log(
    start_msg="⏱ 💾 Install all dependencies for dev, test, doc, automation",
    end_msg="⏰ End 'Install all dependencies for dev, test, doc, automation', elapsed = {elapsed} sec",
)
def pip_install_all():
    """
    cmd: ``pip install -r requirements-dev.txt``
    """
    _try_poetry_export()

    subprocess.run(
        [f"{bin_pip}", "install", "-e", f"{dir_project_root}", "--no-deps"],
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_main}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_dev}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_test}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_doc}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )

    args = [f"{bin_pip}", "install", "-r", f"{path_requirements_automation}"]
    _quite_pip_install_in_ci(args)
    subprocess.run(
        args,
        check=True,
    )
