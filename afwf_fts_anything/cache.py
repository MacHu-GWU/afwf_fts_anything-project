# -*- coding: utf-8 -*-

"""
Disk cache for Alfred Workflow.
"""

from diskcache import Cache

from .paths import dir_cache

cache = Cache(dir_cache.abspath)
