# -*- coding: utf-8 -*-

import pytest
from pydantic import ValidationError
from sayt2.api import StoredField, NgramField, TextField, KeywordField, NumericField
from afwf_fts_anything.exc import MalformedSettingError
from afwf_fts_anything.setting import Setting


def make_movie_fields():
    return [
        StoredField(name="movie_id"),
        NgramField(name="title"),
        TextField(name="description"),
        KeywordField(name="genres"),
        NumericField(name="rating", indexed=True, fast=True),
        StoredField(name="url"),
    ]


class TestSetting:
    def test_basic(self):
        setting = Setting(
            fields=make_movie_fields(),
            title_field="Movie Title: {title} [{genres}]",
            subtitle_field="{description}",
            arg_field="{url}",
            autocomplete_field="{title}",
        )
        assert len(setting.store_fields) == 6
        assert len(setting.searchable_fields) == 4
        assert len(setting.sortable_fields) == 1

    def test_from_dict(self):
        setting = Setting.model_validate(
            {
                "fields": [
                    {"type": "stored", "name": "movie_id"},
                    {"type": "ngram", "name": "title"},
                    {"type": "text", "name": "description"},
                    {"type": "keyword", "name": "genres"},
                    {"type": "numeric", "name": "rating", "indexed": True, "fast": True},
                    {"type": "stored", "name": "url"},
                ],
                "title_field": "Movie Title: {title} [{genres}]",
                "subtitle_field": "{description}",
                "arg_field": "{url}",
            }
        )
        assert len(setting.store_fields) == 6
        assert len(setting.searchable_fields) == 4
        assert len(setting.sortable_fields) == 1

    def test_duplicate_field_names(self):
        with pytest.raises((MalformedSettingError, ValidationError)):
            Setting(fields=[StoredField(name="field1"), StoredField(name="field1")])

    def test_empty_fields_no_title(self):
        # when title_field is not defined, a field named 'title' must exist
        with pytest.raises((MalformedSettingError, ValidationError)):
            Setting(fields=[])

    def test_title_field_not_stored(self):
        # title field exists but stored=False
        with pytest.raises((MalformedSettingError, ValidationError)):
            Setting(fields=[NgramField(name="title", stored=False)])

    def test_title_field_undefined_reference(self):
        # title_field template references a field name not in fields
        with pytest.raises((MalformedSettingError, ValidationError)):
            Setting(
                fields=[StoredField(name="movie_title")],
                title_field="Movie Title: {the_movie_title}, {another_movie_title}",
            )

    def test_title_field_reference_not_stored(self):
        # title_field template references a field that is not stored
        with pytest.raises((MalformedSettingError, ValidationError)):
            Setting(
                fields=[NgramField(name="movie_title", stored=False)],
                title_field="Movie Title: {movie_title}",
            )


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.setting", preview=False)
