# -*- coding: utf-8 -*-

import pytest

from afwf_fts_anything.exc import BuildIndexError
from afwf_fts_anything.paths import path_settings, path_data, dir_index, dir_icon
from afwf_fts_anything.dataset import Dataset
from afwf_fts_anything.handlers.fts import handler


class TestHandler:
    def test_build_index(self):
        dataset = Dataset(
            name="movie",
            path_setting=path_settings,
            path_data=path_data,
            dir_index=dir_index,
            dir_icon=dir_icon,
        )
        handler.build_index(dataset)

        dataset = Dataset(
            name="not-exists",
            path_setting=path_settings,
            path_data=path_data.change("not-exists-data.json"),
            dir_index=dir_index.change(new_basename="not-exists"),
        )
        with pytest.raises(BuildIndexError):
            handler.build_index(dataset)

    def test_parse_query(self):
        assert handler.parse_query("movie ") == dict(dataset_name="movie", query_str="")
        assert handler.parse_query("movie   ") == dict(
            dataset_name="movie", query_str=""
        )
        assert handler.parse_query("movie   ?") == dict(
            dataset_name="movie", query_str="?"
        )
        assert handler.parse_query("movie   hello   world") == dict(
            dataset_name="movie", query_str="hello world"
        )
        assert handler.parse_query("movie   hello , world") == dict(
            dataset_name="movie", query_str="hello world"
        )

    def test_main(self):
        sf = handler.main(
            dataset_name="movie",
            query_str="",
        )
        assert sf.items[0].title == "Full text search 'movie' dataset"

        sf = handler.main(
            dataset_name="movie",
            query_str="?",
        )
        assert sf.items[0].title == "Open 'movie' dataset folder location"

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
