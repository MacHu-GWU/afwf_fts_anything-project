# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

import afwf_fts_anything.cli as cli_mod
from afwf_fts_anything.paths import path_enum

dir_tests = path_enum.dir_package_test_data


def setup_project_home(tmp_path, monkeypatch) -> Path:
    """Create a temp project home with the DataCatalog layout and redirect path_enum."""
    project_home = tmp_path / "project_home"
    project_home.mkdir()
    monkeypatch.setattr(path_enum, "dir_project_home", project_home)

    # new layout: project_home/movie/ is the dataset root
    movie_dir = project_home / "movie"
    movie_dir.mkdir()
    shutil.copy(dir_tests / "movie" / "movie-setting.json", movie_dir / "movie-setting.json")
    shutil.copy(dir_tests / "movie" / "movie-data.json", movie_dir / "movie-data.json")
    icons_dir = movie_dir / "icons"
    icons_dir.mkdir()
    shutil.copy(dir_tests / "movie" / "icons" / "movie-icon.png", icons_dir / "movie-icon.png")

    return project_home


class TestFts:
    def test_fts(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)
        fts = cli_mod.fts.__wrapped__

        # empty query → returns data; last item is "Open error log"
        sf = fts(dataset_name="movie", query="")
        assert len(sf.items) > 1
        assert sf.items[-1].title == "Open error log"

        # "?" → reveal setting file in Finder
        sf = fts(dataset_name="movie", query="?")
        item = sf.items[0]
        assert item.title == "Open 'movie' dataset folder location"
        assert item.variables.get("reveal_file_in_finder") == "y"

        # search hit — Godfather is movie_id=2, icon resolves under icons/
        sf = fts(dataset_name="movie", query="God Father")
        assert len(sf.items) > 0
        assert sf.items[0].arg == "https://www.imdb.com/title/tt0068646"
        assert sf.items[0].icon.path == str(project_home / "movie" / "icons" / "movie-icon.png")

        # index already exists on second call (no rebuild)
        sf = fts(dataset_name="movie", query="God Father")
        assert sf.items[0].arg == "https://www.imdb.com/title/tt0068646"

        # no results
        sf = fts(dataset_name="movie", query="zzznomatchzzz")
        assert sf.items[0].title.startswith("No result found for query:")


class TestListDatasets:
    def test_no_datasets(self, tmp_path, monkeypatch):
        project_home = tmp_path / "empty_home"
        project_home.mkdir()
        monkeypatch.setattr(path_enum, "dir_project_home", project_home)

        sf = cli_mod.list_datasets_for_reset.__wrapped__(dataset_name_query="")
        assert len(sf.items) == 1
        assert sf.items[0].valid is False
        assert "No datasets found" in sf.items[0].title

    def test_list_all(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod.list_datasets_for_reset.__wrapped__(dataset_name_query="")
        assert len(sf.items) == 1
        assert sf.items[0].title == "movie"
        assert "rebuild-index" in sf.items[0].arg
        assert "movie" in sf.items[0].arg

    def test_fuzzy_match(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod.list_datasets_for_reset.__wrapped__(dataset_name_query="mov")
        assert len(sf.items) == 1
        assert sf.items[0].title == "movie"

    def test_fuzzy_no_match_returns_all(self, tmp_path, monkeypatch):
        setup_project_home(tmp_path, monkeypatch)

        sf = cli_mod.list_datasets_for_reset.__wrapped__(dataset_name_query="zzznomatch")
        assert len(sf.items) == 1

    def test_invalid_setting_skipped(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)
        # broken dataset: subdirectory with an unparseable setting file
        broken_dir = project_home / "broken"
        broken_dir.mkdir()
        (broken_dir / "broken-setting.json").write_text("not valid json{{{")

        sf = cli_mod.list_datasets_for_reset.__wrapped__(dataset_name_query="")
        titles = [i.title for i in sf.items]
        assert "movie" in titles
        assert "broken" not in titles


class TestRebuildIndex:
    def test_rebuild_from_local_data(self, tmp_path, monkeypatch):
        project_home = setup_project_home(tmp_path, monkeypatch)

        # build initial index
        cli_mod.rebuild_index("movie")
        dir_index = project_home / "movie" / "movie-index"
        assert dir_index.exists()

        # rebuild clears and recreates the index
        cli_mod.rebuild_index("movie")
        assert dir_index.exists()


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.cli",
        preview=False,
    )
