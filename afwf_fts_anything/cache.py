# -*- coding: utf-8 -*-

"""
Disk cache for Alfred Workflow.
"""

from diskcache import Cache

from .paths import path_enum

cache = Cache(path_enum.dir_cache)
