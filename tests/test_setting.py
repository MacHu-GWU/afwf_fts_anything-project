# -*- coding: utf-8 -*-

import pytest
from afwf_fts_anything.exc import MalformedSettingError
from afwf_fts_anything.setting import Field, Setting


class TestField:
    def test(self):
        with pytest.raises(MalformedSettingError):
            Field(
                name="weight",
                type_is_store=False,
                is_sortable=True,
            )


class TestSetting:
    def test(self):
        setting = Setting(
            fields=[
                Field(
                    name="movie_id",
                    type_is_store=True,
                ),
                Field(
                    name="title",
                    type_is_store=True,
                    type_is_ngram=True,
                ),
                Field(
                    name="description",
                    type_is_store=True,
                    type_is_phrase=True,
                ),
                Field(
                    name="genres",
                    type_is_store=True,
                    type_is_keyword=True,
                ),
                Field(
                    name="rating",
                    type_is_store=True,
                    type_is_numeric=True,
                    is_sortable=True,
                    is_sort_ascending=False,
                ),
                Field(
                    name="url",
                    type_is_store=True,
                ),
            ],
            title_field="Movie Title: {title} [{genres}]",
            subtitle_field="{description}",
            arg_field="{url}",
            autocomplete_field="{title}",
        )
        schema = setting.create_whoosh_schema()
        assert len(setting.store_fields) == 6
        assert len(setting.searchable_fields) == 4
        assert len(setting.sortable_fields) == 1

        data = {
            "title": "The Godfather",
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "genres": "Crime, Drama",
            "url": "https://www.imdb.com/title/tt0068646/",
        }
        assert setting.format_title(data) == "Movie Title: The Godfather [Crime, Drama]"
        assert setting.format_subtitle(data) == data["description"]
        assert setting.format_arg(data) == data["url"]
        assert setting.format_autocomplete(data) == data["title"]

        # from dict
        setting = Setting.from_dict(
            {
                "fields": [
                    {
                        "name": "movie_id",
                        "type_is_store": True,
                    },
                    {
                        "name": "title",
                        "type_is_store": True,
                        "type_is_ngram": True,
                    },
                    {
                        "name": "description",
                        "type_is_store": True,
                        "type_is_phrase": True,
                    },
                    {
                        "name": "genres",
                        "type_is_store": True,
                        "type_is_keyword": True,
                    },
                    {
                        "name": "rating",
                        "type_is_store": True,
                        "type_is_numeric": True,
                        "is_sortable": True,
                        "is_sort_ascending": False,
                    },
                    {
                        "name": "url",
                        "type_is_store": True,
                    },
                ],
                "title_field": "Movie Title: {title} [{genres}]",
                "subtitle_field": "{description}",
                "arg_field": "{url}",
            }
        )
        assert len(setting.store_fields) == 6
        assert len(setting.searchable_fields) == 4
        assert len(setting.sortable_fields) == 1

        # you have duplicate field names in your fields: ['field1', 'field1']
        with pytest.raises(MalformedSettingError):
            Setting(fields=[Field(name="field1"), Field(name="field1")])

        # you have to specify one and only one index type for column 'title', valid types are: ngram, phrase, keyword.
        with pytest.raises(MalformedSettingError):
            Setting(
                fields=[
                    Field(
                        name="title",
                        type_is_keyword=True,
                        type_is_phrase=True,
                    )
                ],
            )

        # when title_field is not defined, you have to have a field called 'title' in your data fields, here's your data fields: []
        with pytest.raises(MalformedSettingError):
            Setting(fields=[])

        # the title field is not a stored field!
        with pytest.raises(MalformedSettingError):
            Setting(
                fields=[
                    Field(
                        name="title",
                        type_is_store=False,
                    )
                ]
            )

        # your title_field = 'Movie Title: {the_movie_title}, {another_movie_title}' contains a field name 'the_movie_title', but it is not defined in your fields: ['movie_title']
        with pytest.raises(MalformedSettingError):
            Setting(
                fields=[
                    Field(
                        name="movie_title",
                    )
                ],
                title_field="Movie Title: {the_movie_title}, {another_movie_title}",
            )

        # our title_field = 'Movie Title: {movie_title}' contains a field name 'movie_title', but this field is not stored: Field(name='movie_title', type_is_store=False, type_is_ngram=False, type_is_phrase=False, type_is_keyword=False, ngram_minsize=2, ngram_maxsize=10, keyword_lowercase=True, keyword_commas=True)
        with pytest.raises(MalformedSettingError):
            Setting(
                fields=[
                    Field(
                        name="movie_title",
                        type_is_store=False,
                    )
                ],
                title_field="Movie Title: {movie_title}",
            )


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.setting", preview=False)
