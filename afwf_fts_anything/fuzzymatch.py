# -*- coding: utf-8 -*-

"""
Fuzzy match module for workflow item sorting.
"""

import typing as T
import afwf
from fuzzywuzzy import process


MEMBER = T.TypeVar("MEMBER")


class FuzzyMatcher(
    T.Generic[MEMBER],
):
    """
    A simple wrapper around fuzzywuzzy search.

    The mapper is a dict of key and member. The key is used for fuzzy search.
    """

    def __init__(self, mapper: T.Dict[str, MEMBER]):
        self.mapper = mapper
        self.keys = list(mapper.keys())

    def match(self, query: str, limit: int = 20) -> T.List[MEMBER]:
        """ """
        return [
            self.mapper[key]
            for key, score in process.extract(query, self.keys, limit=limit)
        ]


class ItemFuzzyMatcher(FuzzyMatcher[afwf.Item]):
    pass
