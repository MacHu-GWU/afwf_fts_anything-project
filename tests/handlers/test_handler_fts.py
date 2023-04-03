# -*- coding: utf-8 -*-

from afwf_fts_anything.paths import path_settings, path_data, dir_index, dir_icon
from afwf_fts_anything.handlers.fts import handler
from rich import print as rprint

class TestHandler:
    def test(self):
        sf = handler.main(
            dataset_name="movie",
            query_str="",
        )
        assert sf.items[0].title == "Full text search 'movie' dataset"

        sf = handler.main(
            dataset_name="movie",
            query_str="God Father",
        )
        assert sf.items[0].arg == "2"

        sf = handler.main(
            dataset_name="movie",
            query_str="this movie doesn't exists, don't ever try it",
        )
        assert sf.items[0].title.startswith("No result found for query:")


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.handlers.fts", preview=False)
