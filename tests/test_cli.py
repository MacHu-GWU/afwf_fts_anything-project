# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

import afwf_fts_anything.cli as cli_mod
from afwf_fts_anything.paths import path_enum

dir_tests = Path(__file__).parent


class TestFts:
    def test_fts(self, tmp_path, monkeypatch):
        # Set up a temp project home and redirect path_enum there
        project_home = tmp_path / "project_home"
        project_home.mkdir()
        monkeypatch.setattr(path_enum, "dir_project_home", project_home)

        # Copy setting + data into the temp project home
        shutil.copy(
            dir_tests / "movie-setting.json", project_home / "movie-setting.json"
        )
        shutil.copy(dir_tests / "movie-data.json", project_home / "movie-data.json")

        # Bypass log_error to let exceptions surface in tests
        fts = cli_mod._fts.__wrapped__

        # empty query → prompt item
        sf = fts(dataset_name="movie", query="")
        assert sf.items[0].title == "Full text search 'movie' dataset"

        # "?" → reveal setting file in Finder
        sf = fts(dataset_name="movie", query="?")
        item = sf.items[0]
        assert item.title == "Open 'movie' dataset folder location"
        assert item.variables.get("reveal_file_in_finder") == "y"

        # search hit → index is built on first call, Godfather is movie_id=2
        sf = fts(dataset_name="movie", query="God Father")
        assert len(sf.items) > 0
        assert sf.items[0].arg == "2"

        # index already exists on second call (no rebuild)
        sf = fts(dataset_name="movie", query="God Father")
        assert sf.items[0].arg == "2"

        # no results
        sf = fts(dataset_name="movie", query="zzznomatchzzz")
        assert sf.items[0].title.startswith("No result found for query:")


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.cli",
        preview=False,
    )
