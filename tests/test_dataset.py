# -*- coding: utf-8 -*-

import io
import json
import zipfile

from afwf_fts_anything.paths import path_enum
from afwf_fts_anything.dataset import Dataset

dir_tests = path_enum.dir_unit_test
path_setting = dir_tests / "movie-setting.json"
path_data = dir_tests / "movie-data.json"
dir_index = dir_tests / "movie-index"
dir_icon = dir_tests / "movie-icon"


def make_dataset() -> Dataset:
    return Dataset(
        name="movie",
        path_setting=path_setting,
        path_data=path_data,
        dir_index=dir_index,
        dir_icon=dir_icon,
    )


class TestDatasetPaths:
    def test_default_paths(self):
        ds = Dataset(name="movie")
        assert ds._path_setting.name == "movie-setting.json"
        assert ds._path_data.name == "movie-data.json"
        assert ds._dir_index.name == "movie-index"
        assert ds._dir_icon.name == "movie-icon"


class TestExtractJsonFromZip:
    def test_single_json(self):
        records = [{"id": 1, "title": "hello"}]
        raw_json = json.dumps(records).encode()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("data.json", raw_json)
        zip_bytes = buf.getvalue()

        result = Dataset._extract_json_from_zip(zip_bytes)
        assert json.loads(result) == records

    def test_multiple_files_picks_first_json(self):
        records = [{"id": 2}]
        raw_json = json.dumps(records).encode()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", b"ignore me")
            zf.writestr("records.json", raw_json)
        zip_bytes = buf.getvalue()

        result = Dataset._extract_json_from_zip(zip_bytes)
        assert json.loads(result) == records


class TestSaveData:
    def test_save_plain(self, tmp_path):
        ds = Dataset(name="test", path_data=tmp_path / "data.json")
        raw = b'[{"id": 1}]'
        ds._save_data(raw, is_zip=False)
        assert json.loads(ds._path_data.read_bytes()) == [{"id": 1}]

    def test_save_zip(self, tmp_path):
        records = [{"id": 99}]
        raw_json = json.dumps(records).encode()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("data.json", raw_json)
        zip_bytes = buf.getvalue()

        ds = Dataset(name="test", path_data=tmp_path / "data.json")
        ds._save_data(zip_bytes, is_zip=True)
        assert json.loads(ds._path_data.read_bytes()) == records


class TestDatasetIndexing:
    def test_search(self):
        ds = make_dataset()
        ds.build_index(data=ds.get_data(), rebuild=True)

        # cache hit: same result on repeated calls
        for _ in range(3):
            results = ds.search("god father")
            assert results[0]["movie_id"] == 2

        # sort by rating descending: top-3 drama results must be rated 9.2, 9.2, 9.0
        results = ds.search("drama", limit=3)
        ratings = [r["rating"] for r in results]
        assert ratings == sorted(ratings, reverse=True)
        assert ratings[0] == 9.2
        assert ratings[1] == 9.2
        assert ratings[2] == 9.0


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.dataset",
        preview=False,
    )
