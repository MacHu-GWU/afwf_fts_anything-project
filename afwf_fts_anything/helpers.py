# -*- coding: utf-8 -*-

import typing as T


def is_no_overlap(list_of_container: T.List[list]) -> bool:
    """
    Test if there's no common item in several set.
    """
    return (
        sum([len(container) for container in list_of_container])
        == len(set.union(*[set(container) for container in list_of_container]))
    )
