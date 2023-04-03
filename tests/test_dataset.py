# -*- coding: utf-8 -*-

from afwf_fts_anything.paths import path_settings, path_data, dir_index
from afwf_fts_anything.dataset import Dataset


class TestDataset:
    def test_property(self):
        dataset = Dataset(name="movie")
        assert dataset._path_data.basename == "movie-data.json"
        assert dataset._path_setting.basename == "movie-setting.json"
        assert dataset._dir_index.basename == "movie-whoosh_index"

    def test_indexing(self):
        dataset = Dataset(
            name="movie",
            path_setting=path_settings,
            path_data=path_data,
            dir_index=dir_index,
        )
        dataset.build_index(rebuild=True)

        # cache should work
        for _ in range(3):
            doc_list = dataset.search("god father")
            assert doc_list[0]["movie_id"] == 2

        doc_list = dataset.search("drama", limit=3)
        assert [doc["movie_id"] for doc in doc_list] == [1, 2, 3]


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.dataset", preview=False)
