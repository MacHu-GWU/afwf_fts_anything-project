# -*- coding: utf-8 -*-

import io
import json
import zipfile

from afwf_fts_anything.dataset import Dataset
from afwf_fts_anything.paths import path_enum

dir_movie = path_enum.dir_package_test_data_movie


def make_dataset() -> Dataset:
    return Dataset(name="movie", dir_root=dir_movie)


class TestDatasetPaths:
    def test_computed_paths(self, tmp_path):
        ds = Dataset(name="movie", dir_root=tmp_path)
        assert ds.path_setting == tmp_path / "movie-setting.json"
        assert ds.path_data == tmp_path / "movie-data.json"
        assert ds.dir_index == tmp_path / "movie-index"
        assert ds.get_icon("poster.png") == tmp_path / "icons" / "poster.png"
        assert ds.get_icon("poster") == tmp_path / "icons" / "poster"


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
        ds = Dataset(name="test", dir_root=tmp_path)
        raw = b'[{"id": 1}]'
        ds._save_data(raw, is_zip=False)
        assert json.loads(ds.path_data.read_bytes()) == [{"id": 1}]

    def test_save_zip(self, tmp_path):
        records = [{"id": 99}]
        raw_json = json.dumps(records).encode()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("data.json", raw_json)
        zip_bytes = buf.getvalue()

        ds = Dataset(name="test", dir_root=tmp_path)
        ds._save_data(zip_bytes, is_zip=True)
        assert json.loads(ds.path_data.read_bytes()) == records


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
