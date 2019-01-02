# -*- coding: utf-8 -*-

import json
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


def dump_json(data, path):
    with open(path, "wb") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True).encode("utf-8"))


def load_json(path):
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))
