# -*- coding: utf-8 -*-

import pytest
from afwf_fts_anything.exc import MalformedSetting
from afwf_fts_anything.setting import Field, Setting


class TestSetting:
    def test(self):
        setting = Setting(
            fields=[
                Field(
                    name="title",
                    type_is_store=True,
                    type_is_ngram=True,
                ),
                Field(
                    name="subtitle",
                    type_is_store=True,
                    type_is_phrase=True,
                ),
                Field(
                    name="genres",
                    type_is_store=True,
                    type_is_keyword=True,
                ),
                Field(
                    name="url",
                    type_is_store=True,
                ),
            ],
        )
        schema = setting.create_whoosh_schema()
        assert len(setting.store_fields) == 4
        assert len(setting.searchable_fields) == 3

        # you have duplicate field names in your fields: ['field1', 'field1']
        with pytest.raises(MalformedSetting):
            Setting(fields=[Field(name="field1"), Field(name="field1")])

        # you have to specify one and only one index type for column 'title', valid types are: ngram, phrase, keyword.
        with pytest.raises(MalformedSetting):
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
        with pytest.raises(MalformedSetting):
            Setting(fields=[])

        # the title field is not a stored field!
        with pytest.raises(MalformedSetting):
            Setting(
                fields=[
                    Field(
                        name="title",
                        type_is_store=False,
                    )
                ]
            )

        # your title_field = 'Movie Title: {the_movie_title}, {another_movie_title}' contains a field name 'the_movie_title', but it is not defined in your fields: ['movie_title']
        with pytest.raises(MalformedSetting):
            Setting(
                fields=[
                    Field(
                        name="movie_title",
                    )
                ],
                title_field="Movie Title: {the_movie_title}, {another_movie_title}",
            )

        # our title_field = 'Movie Title: {movie_title}' contains a field name 'movie_title', but this field is not stored: Field(name='movie_title', type_is_store=False, type_is_ngram=False, type_is_phrase=False, type_is_keyword=False, ngram_minsize=2, ngram_maxsize=10, keyword_lowercase=True, keyword_commas=True)
        with pytest.raises(MalformedSetting):
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
