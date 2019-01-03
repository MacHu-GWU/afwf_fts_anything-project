# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest

import shutil
from pathlib_mate import PathCls as Path
from superjson import json
from afwf_fts_anything.dataset import DataSet, Setting, ALFRED_FTS


class TestMovieDataset(object):
    dataset_name = None
    data = None
    setting = None

    @classmethod
    def setup_class(cls):
        dataset_name = "movie"
        movie_data = [
            dict(movie_id=1, title="The Shawshank Redemption",
                 description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                 genres="Drama"),
            dict(movie_id=2, title="The Godfather",
                 description="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                 genres="Crime, Drama"),
            dict(movie_id=3, title="The Godfather: Part II",
                 description="The early life and career of Vito Corleone in 1920s New York City is portrayed, while his son, Michael, expands and tightens his grip on the family crime syndicate.",
                 genres="Crime, Drama"),
        ]
        movie_setting_data = {
            "columns": [
                {
                    "name": "movie_id",
                    "type_is_store": True,
                },
                {
                    "name": "title",
                    "type_is_ngram": True,
                    "ngram_minsize": 2,
                    "ngram_maxsize": 10,
                },
                {
                    "name": "description",
                    "type_is_phrase": True,
                },
                {
                    "name": "genres",
                    "type_is_keyword": True,
                    "keyword_lowercase": True,
                },
            ],
            "title_field": "{title} ({genres})",
            "subtitle_field": "description",
            "arg_field": "movie_id",
            "autocomplete_field": "{movie_id} - {title}",
            "icon_field": Path(ALFRED_FTS, "movie-icon.png").abspath,
        }
        movie_setting = Setting.from_dict(movie_setting_data)
        cls.dataset_name = dataset_name
        cls.data = movie_data
        cls.setting = movie_setting

        dataset = DataSet(name=dataset_name, data=None,
                          setting=Setting(skip_post_init=True))
        data_file_path = dataset.get_data_file_path()
        setting_file_path = dataset.get_setting_file_path()
        index_dir = dataset.get_index_dir_path()
        if index_dir.exists():
            shutil.rmtree(index_dir.abspath)
        json.dump(movie_data, data_file_path.abspath,
                  indent=4, sort_keys=True, ensure_ascii=False, overwrite=True, verbose=False)
        json.dump(movie_setting_data, setting_file_path.abspath,
                  indent=4, sort_keys=True, ensure_ascii=False, overwrite=True, verbose=False)

    def test_search(self):
        dataset = DataSet(
            name=self.dataset_name,
            data=self.data,
            setting=self.setting,
        )
        idx = dataset.get_index()
        dataset.build_index(idx)

        result = dataset.search("redemption")
        assert len(result) == 1

        result = dataset.search("godfather")
        assert len(result) == 2

        result = dataset.search("empire")
        assert len(result) == 1

        result = dataset.search("family")
        assert len(result) == 1

        result = dataset.search("crime")
        assert len(result) == 2

        result = dataset.search("drama")
        assert len(result) == 3


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
