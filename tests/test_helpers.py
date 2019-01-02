# -*- coding: utf-8 -*-

import pytest
from afwf_fts_anything import helpers


def test_is_no_overlap():
    assert helpers.is_no_overlap([1, 2], [3, 4])
    assert helpers.is_no_overlap([1, 2], [2, 3]) is False


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
