# -*- coding: utf-8 -*-

import subprocess
from .config import config
from .paths import (
    PACKAGE_NAME,
    bin_pip,
    dir_project_root,
    path_git_repo_main_py,
    path_git_repo_info_plist,
)
from .deps import _try_poetry_export
from .logger import logger

path_workflow_info_plist = config.dir_workflow / "info.plist"
path_workflow_main_py = config.dir_workflow / "main.py"
dir_workflow_lib = config.dir_workflow / "lib"


@logger.pretty_log()
def build_wf():
    """
    Build Alfred Workflow release from source code. Basically it creates:

    - user.workflow.../main.py
    - user.workflow.../lib
    - ${dir_project_root}/info.plist
    """
    # delete user.workflow.../main.py
    path_workflow_main_py.remove_if_exists()
    # delete user.workflow.../lib
    dir_workflow_lib.remove_if_exists()
    # delete ${dir_project_roo}/info.plist
    path_git_repo_info_plist.remove_if_exists()

    # create user.workflow.../main.py
    path_git_repo_main_py.copyto(path_workflow_main_py)

    # create user.workflow.../lib/
    _try_poetry_export()
    with dir_project_root.temp_cwd():
        args = [
            f"{bin_pip}",
            "install",
            f"{dir_project_root}",
            f"--target={dir_workflow_lib}",
        ]
        subprocess.run(args)

    # create info.plist
    path_workflow_info_plist.copyto(path_git_repo_info_plist)


@logger.pretty_log()
def refresh_code():
    """
    This shell script only re-build the main.py and the source code
    to Alfred Workflow preference directory, without install any dependencies

    It allows developer to quickly test the latest code with real Alfred UI
    You should run this script everything you update your source code
    """
    # delete user.workflow.../main.py
    path_workflow_main_py.remove_if_exists()
    # delete user.workflow.../lib/${PACKAGE_NAME}/
    dir_workflow_lib.joinpath(PACKAGE_NAME).remove_if_exists()
    # delete user.workflow.../lib/${PACKAGE_NAME}-${VERSION}.dist-info/
    for p in dir_workflow_lib.iterdir():
        if p.basename.startswith(f"{PACKAGE_NAME}-") and p.basename.endswith(
            ".dist-info"
        ):
            p.remove_if_exists()

    # create user.workflow.../main.py
    path_git_repo_main_py.copyto(path_workflow_main_py)
    _try_poetry_export()
    with dir_project_root.temp_cwd():
        args = [
            f"{bin_pip}",
            "install",
            f"{dir_project_root}",
            "--no-dependencies",
            f"--target={dir_workflow_lib}",
        ]
        subprocess.run(args)


@logger.pretty_log(
    start_msg="🪲 Debug Script Filter",
    end_msg="🪲 End 'Debug Script Filter', elapsed = {elapsed} sec",
)
def debug(
    bin_python: str,
    handler_id: str,
    query: str,
):
    """
    This is a utility function to debug an Alfred Workflow.

    :param bin_python:
    :param handler_id:
    :param query:
    """
    args = [
        bin_python,
        "main.py",
        f"{handler_id} {query}",
    ]
    cmd = " ".join(args)
    logger.info(f"run: {cmd}")
    with config.dir_workflow.temp_cwd():
        subprocess.run(args)
