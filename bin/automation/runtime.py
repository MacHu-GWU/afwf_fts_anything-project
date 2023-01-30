# -*- coding: utf-8 -*-

"""
**"Runtime" Definition**

Runtime is where you execute your code. For example, if this code is running
in a CI build environment, then the runtime is "ci". If this code is running
on your local laptop, then the runtime is "local". If this code is running on
AWS Lambda, then the runtime is "lbd"

This module automatically detect what is the current runtime.

.. note::

    This module is "ZERO-DEPENDENCY".
"""

import os

from .logger import logger


class RuntimeEnum:
    """
    This code will only be run either from local laptop or CI environment.
    It won't be run from Lambda Function. For EC2, it considers EC2 the
    same as your local laptop.
    """

    local = "local"
    ci = "ci"


emoji_mapper = {
    RuntimeEnum.local: "💻",
    RuntimeEnum.ci: "🔨",
}


# In alfred workflow project, we usually use GitHub Action as the CI build environment
# See https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
if "CI" in os.environ:
    CURRENT_RUNTIME = RuntimeEnum.ci
    IS_CI = True
    IS_LOCAL = False
else:
    CURRENT_RUNTIME = RuntimeEnum.local
    IS_CI = False
    IS_LOCAL = True


def print_runtime_info():
    logger.info(f"Current runtime is {emoji_mapper[CURRENT_RUNTIME]} {CURRENT_RUNTIME!r}")
