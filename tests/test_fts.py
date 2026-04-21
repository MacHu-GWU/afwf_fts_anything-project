# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from afwf_fts_anything.fts import fts

# tests/ is the DataCatalog root; tests/movie/ is the "movie" dataset root
dir_tests = Path(__file__).parent


class TestFtsRevealSetting:
    def test_question_mark_query(self):
        items = fts(dataset_name="movie", query="?", dir_datacatalog_root=dir_tests)
        assert len(items) == 1
        item = items[0]
        assert "movie" in item.title
        assert item.variables.get("reveal_file_in_finder") == "y"

    def test_question_mark_points_to_setting_file(self):
        items = fts(dataset_name="movie", query="?", dir_datacatalog_root=dir_tests)
        revealed = items[0].variables.get("reveal_file_in_finder_path")
        assert revealed is not None
        assert revealed.endswith("movie-setting.json")


class TestFtsSearch:
    def test_empty_query_returns_all_docs(self):
        items = fts(dataset_name="movie", query="", dir_datacatalog_root=dir_tests)
        # empty query shows the full dataset (excluding the error-log item which is not added
        # here because path_error_log=None)
        assert len(items) > 1

    def test_empty_query_no_error_log_item_without_path(self):
        items = fts(dataset_name="movie", query="", dir_datacatalog_root=dir_tests)
        titles = [i.title for i in items]
        assert "Open error log" not in titles

    def test_empty_query_appends_error_log_item_when_path_given(self, tmp_path):
        log_path = tmp_path / "error.log"
        items = fts(
            dataset_name="movie",
            query="",
            dir_datacatalog_root=dir_tests,
            path_error_log=log_path,
        )
        assert items[-1].title == "Open error log"
        assert items[-1].variables.get("open_file") == "y"

    def test_search_hit(self):
        items = fts(dataset_name="movie", query="God Father", dir_datacatalog_root=dir_tests)
        assert len(items) > 0
        assert items[0].arg == "2"

    def test_search_hit_icon_is_resolved(self):
        items = fts(dataset_name="movie", query="God Father", dir_datacatalog_root=dir_tests)
        expected_icon = str(dir_tests / "movie" / "icons" / "movie-icon.png")
        assert items[0].icon.path == expected_icon

    def test_no_results_for_nonsense_query(self):
        items = fts(dataset_name="movie", query="zzznomatchzzz", dir_datacatalog_root=dir_tests)
        assert len(items) == 1
        assert items[0].title.startswith("No result found for query:")

    def test_index_rebuilt_on_second_call(self):
        # index already exists after the first test run — result should be stable
        items = fts(dataset_name="movie", query="God Father", dir_datacatalog_root=dir_tests)
        assert items[0].arg == "2"


class TestFtsErrorCases:
    def test_nonexistent_dataset_raises(self, tmp_path):
        # tmp_path has no "ghost" subdirectory → build_index will fail
        with pytest.raises(Exception):
            fts(dataset_name="ghost", query="anything", dir_datacatalog_root=tmp_path)

    def test_missing_data_file_raises(self, tmp_path):
        # dataset dir exists with a valid setting (no data_url) but no data file;
        # get_data() will call download_data() which raises ValueError when data_url is absent
        import json
        dataset_dir = tmp_path / "empty"
        dataset_dir.mkdir()
        setting = {
            "fields": [{"type": "stored", "name": "id"}],
            "title_field": "{id}",
            "subtitle_field": "{id}",
            "arg_field": "{id}",
            "autocomplete_field": "{id}",
        }
        (dataset_dir / "empty-setting.json").write_text(json.dumps(setting))
        with pytest.raises(Exception):
            fts(dataset_name="empty", query="anything", dir_datacatalog_root=tmp_path)


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.fts",
        preview=False,
    )
