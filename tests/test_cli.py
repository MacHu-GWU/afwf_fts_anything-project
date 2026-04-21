# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

import afwf_fts_anything.cli as cli_mod
from afwf_fts_anything.paths import path_enum

dir_tests = Path(__file__).parent


def setup_project_home(tmp_path, monkeypatch) -> Path:
    """Create a temp project home with movie dataset files and redirect path_enum."""
    project_home = tmp_path / "project_home"
    project_home.mkdir()
    monkeypatch.setattr(path_enum, "dir_project_home", project_home)

    shutil.copy(dir_tests / "movie-setting.json", project_home / "movie-setting.json")
    shutil.copy(dir_tests / "movie-data.json", project_home / "movie-data.json")
    dir_icon = project_home / "movie-icon"
    dir_icon.mkdir()
    shutil.copy(dir_tests / "movie-icon.png", dir_icon / "movie-icon.png")

    return project_home


class TestFts:
    def test_fts(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)
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
        assert sf.items[0].icon.path == str(project_home / "movie-icon" / "movie-icon.png")

        # index already exists on second call (no rebuild)
        sf = fts(dataset_name="movie", query="God Father")
        assert sf.items[0].arg == "2"

        # no results
        sf = fts(dataset_name="movie", query="zzznomatchzzz")
        assert sf.items[0].title.startswith("No result found for query:")


class TestListDatasets:
    def test_no_datasets(self, tmp_path, monkeypatch):
        project_home = tmp_path / "empty_home"
        project_home.mkdir()
        monkeypatch.setattr(path_enum, "dir_project_home", project_home)

        sf = cli_mod._list_datasets.__wrapped__(query="")
        assert len(sf.items) == 1
        assert sf.items[0].valid is False
        assert "No datasets found" in sf.items[0].title

    def test_list_all(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod._list_datasets.__wrapped__(query="")
        assert len(sf.items) == 1
        assert sf.items[0].title == "movie"
        # pressing Enter triggers rebuild-index
        assert "rebuild-index" in sf.items[0].arg
        assert "movie" in sf.items[0].arg

    def test_fuzzy_match(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod._list_datasets.__wrapped__(query="mov")
        assert len(sf.items) == 1
        assert sf.items[0].title == "movie"

    def test_fuzzy_no_match_returns_all(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod._list_datasets.__wrapped__(query="zzznomatch")
        # falls back to full list
        assert len(sf.items) == 1

    def test_invalid_setting_skipped(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)
        # write a broken setting file
        (project_home / "broken-setting.json").write_text("not valid json{{{")

        sf = cli_mod._list_datasets.__wrapped__(query="")
        titles = [i.title for i in sf.items]
        assert "movie" in titles
        assert "broken" not in titles


class TestRebuildIndex:
    def test_rebuild_from_local_data(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)
        dataset_name = "movie"

        # build initial index
        cli_mod._rebuild_index(dataset_name)
        dir_index = project_home / "movie-index"
        assert dir_index.exists()

        # rebuild clears and recreates the index
        cli_mod._rebuild_index(dataset_name)
        assert dir_index.exists()


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.cli",
        preview=False,
    )
