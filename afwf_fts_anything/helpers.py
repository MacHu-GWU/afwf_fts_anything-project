# -*- coding: utf-8 -*-

import hashlib


def md5_file(path):
    """
    Get md5 check sum of a file.
    """
    m = hashlib.md5()
    with open(path, "rb") as f:
        b = f.read()
        m.update(b)
    return m.hexdigest()


def is_no_overlap(*set_list):
    """
    Test if there's no common item in several set.
    """
    return sum([len(s) for s in set_list]) == len(set.union(*[set(s) for s in set_list]))
