# -*- coding: utf-8 -*-

import subprocess

from .paths import (
    bin_pytest,
    dir_tests,
    dir_htmlcov,
    PACKAGE_NAME,
)
from .config import config
from .logger import logger


@logger.pretty_log(
    start_msg="⏱ 🧪 Run Unit Test",
    end_msg="⏰ End 'Run Unit Test', elapsed = {elapsed} sec",
)
def run_unit_test():
    try:
        args = [
            f"{bin_pytest}",
            f"{dir_tests}",
            "-s",
        ]
        subprocess.run(args, check=True)
        logger.info("✅ Unit Test Succeeded!")
    except Exception as e:
        logger.error("🔥 Unit Test Failed!")
        raise e


@logger.pretty_log(
    start_msg="⏱ 🧪 Run Code Coverage Test",
    end_msg="⏰ End 'Run Code Coverage Test', elapsed = {elapsed} sec",
)
def run_cov_test():
    args = [
        f"{bin_pytest}",
        f"{dir_tests}",
        "-s",
        f"--cov={PACKAGE_NAME}",
        "--cov-report",
        "term-missing",
        "--cov-report",
        f"html:{dir_htmlcov}",
    ]
    try:
        subprocess.run(args, check=True)
        logger.info("✅ Code Coverage Test Succeeded!")
    except Exception as e:
        logger.error("🔥 Code Coverage Test Failed!")
        raise e
