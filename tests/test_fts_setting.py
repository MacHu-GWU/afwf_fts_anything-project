# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import PathCls as Path
from afwf_fts_anything.constant import ALFRED_FTS
from afwf_fts_anything.fts_setting import ColumnSetting, Setting


class TestColumnSetting(object):
    def test_type(self):
        with pytest.raises(ValueError):
            ColumnSetting(name="a")
        with pytest.raises(ValueError):
            ColumnSetting(name="a",
                type_is_ngram=True, type_is_phrase=True, type_is_keyword=True)


class TestSetting(object):
    setting1 = Setting(
        columns=[
            ColumnSetting(name="movie_id", type_is_store=True),
            ColumnSetting(name="title", type_is_ngram=True),
            ColumnSetting(name="description", type_is_phrase=True),
            ColumnSetting(name="genres", type_is_keyword=True),
        ],
        title_field="title",
        subtitle_field="description",
        arg_field="movie_id",
        autocomplete_field="{movie_id} - {title}",
        icon_field=Path(ALFRED_FTS, "movie-icon.png").abspath,
    )
    setting2 = Setting.from_dict({
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
            "title_field": "title",
            "subtitle_field": "description",
            "arg_field": "movie_id",
            "autocomplete_field": "{movie_id} - {title}",
            "icon_field": Path(ALFRED_FTS, "movie-icon.png").abspath,
    })

    def test_columns_property(self):
        assert self.setting1.store_columns == ["movie_id", ]
        assert self.setting1.ngram_columns == ["title", ]
        assert self.setting1.phrase_columns == ["description", ]
        assert self.setting1.keyword_columns == ["genres", ]
        assert self.setting1.searchable_columns == ["title", "description", "genres"]

    def test_create_whoosh_schema(self):
        schema = self.setting1.create_whoosh_schema()

    def test_convert_to_item(self):
        item = self.setting1.convert_to_item(dict(
            movie_id=1, title="The Title", description="The Description", genres="Act Bio",
        ))
        assert item.title == "The Title"
        assert item.subtitle == "The Description"
        assert item.arg == "1"
        assert item.autocomplete == "1 - The Title"
        assert item.icon == Path(ALFRED_FTS, "movie-icon.png").abspath


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
