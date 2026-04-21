# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from afwf_fts_anything.data_catalog import DataCatalog, DatasetMeta, DatasetMetaStatusEnum

dir_tests = Path(__file__).parent


class TestDatasetMeta:
    def test_is_valid_true(self):
        meta = DatasetMeta(name="x", status=DatasetMetaStatusEnum.setting_valid)
        assert meta.is_valid is True

    def test_is_valid_false_for_invalid(self):
        meta = DatasetMeta(name="x", status=DatasetMetaStatusEnum.setting_invalid)
        assert meta.is_valid is False

    def test_is_valid_false_for_not_found(self):
        meta = DatasetMeta(name="x", status=DatasetMetaStatusEnum.setting_not_found)
        assert meta.is_valid is False


class TestDataCatalogGetDataset:
    def test_get_dataset(self):
        catalog = DataCatalog(dir_root=dir_tests)
        ds = catalog.get_dataset("movie")
        assert ds.name == "movie"
        assert ds.dir_root == dir_tests / "movie"


class TestDataCatalogScan:
    def test_valid_dataset(self):
        # tests/movie/ has a well-formed movie-setting.json → should be valid
        catalog = DataCatalog(dir_root=dir_tests)
        metas = catalog.scan()
        movie = next((m for m in metas if m.name == "movie"), None)
        assert movie is not None
        assert movie.status == DatasetMetaStatusEnum.setting_valid
        assert movie.is_valid is True

    def test_invalid_setting(self, tmp_path):
        # setting file exists but contains malformed JSON
        dataset_dir = tmp_path / "broken"
        dataset_dir.mkdir()
        (dataset_dir / "broken-setting.json").write_text("not valid json{{{")

        catalog = DataCatalog(dir_root=tmp_path)
        metas = catalog.scan()
        assert len(metas) == 1
        assert metas[0].name == "broken"
        assert metas[0].status == DatasetMetaStatusEnum.setting_invalid
        assert metas[0].is_valid is False

    def test_dir_without_setting_is_skipped(self, tmp_path):
        # a subdirectory with no setting file is not counted
        (tmp_path / "nodataset").mkdir()

        catalog = DataCatalog(dir_root=tmp_path)
        assert catalog.scan() == []

    def test_plain_files_are_ignored(self, tmp_path):
        # non-directory entries at the root level are ignored
        (tmp_path / "readme.txt").write_text("hello")

        catalog = DataCatalog(dir_root=tmp_path)
        assert catalog.scan() == []

    def test_results_sorted_by_name(self, tmp_path):
        for name in ("zebra", "alpha", "middle"):
            d = tmp_path / name
            d.mkdir()
            shutil.copy(dir_tests / "movie" / "movie-setting.json", d / f"{name}-setting.json")

        catalog = DataCatalog(dir_root=tmp_path)
        names = [m.name for m in catalog.scan()]
        assert names == sorted(names)

    def test_mixed_valid_and_invalid(self, tmp_path):
        # one valid, one broken — both returned with correct statuses
        good = tmp_path / "good"
        good.mkdir()
        shutil.copy(dir_tests / "movie" / "movie-setting.json", good / "good-setting.json")

        bad = tmp_path / "bad"
        bad.mkdir()
        (bad / "bad-setting.json").write_text("{invalid")

        catalog = DataCatalog(dir_root=tmp_path)
        metas = {m.name: m for m in catalog.scan()}
        assert metas["good"].status == DatasetMetaStatusEnum.setting_valid
        assert metas["bad"].status == DatasetMetaStatusEnum.setting_invalid


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.data_catalog",
        preview=False,
    )
