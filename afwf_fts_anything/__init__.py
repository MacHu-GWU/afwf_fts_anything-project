# -*- coding: utf-8 -*-

from ._version import __version__

__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"
__chore__ = "dc2ba0d33e28cbfd762ab8579bcb8483"

try:
    from .workflow import wf
except ImportError: # pragma: no cover
    pass