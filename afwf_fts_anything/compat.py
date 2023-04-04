# -*- coding: utf-8 -*-

try:
    from cached_property import cached_property
except ImportError:
    from functools import cached_property
