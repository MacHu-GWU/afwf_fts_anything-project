# -*- coding: utf-8 -*-


from afwf_fts_anything.helpers import is_no_overlap


def test_is_no_overlap():
    assert is_no_overlap([[1, 2], [3, 4]]) is True
    assert is_no_overlap([[1, 2], [2, 3]]) is False


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.helpers", preview=False)
