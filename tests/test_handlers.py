#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from workflow import Workflow3
from afwf_fts_anything.handlers import main
from afwf_fts_anything.handlers import MSG_FOUND_NOTHING


class TestSearch(object):
    def test_no_argument(self):
        wf = Workflow3()
        main(wf, args=["movie"])
        assert len(wf._items) == 1
        item = wf._items[0]
        assert "Search in Dataset" in item.title

    def test_found_nothing(self):
        wf = Workflow3()
        main(wf, args=["movie", "YouCanNotFindMe"])
        assert len(wf._items) == 1
        item = wf._items[0]
        assert item.title == MSG_FOUND_NOTHING

    def test_found(self):
        wf = Workflow3()
        main(wf, args=["movie", "Godfather"])
        assert len(wf._items) == 2
        for item in wf._items:
            print(item.title)

    # def test_temp(self):
    #     wf = Workflow3()
    #     main(wf, args=["d2skills", "sor"])
    #     for item in wf._items:
    #         print(item.title)
    #         print(item.subtitle)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
