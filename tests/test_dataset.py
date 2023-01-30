# -*- coding: utf-8 -*-


from afwf_fts_anything.dataset import Dataset


class TestDataset:
    def test(self):
        dataset = Dataset(
            name="movie"
        )
        assert dataset.path_data.basename == "movie-data.json"
        assert dataset.path_setting.basename == "movie-setting.json"
        assert dataset.dir_index.basename == "movie-whoosh_index"





if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(__file__, "afwf_fts_anything.dataset", preview=False)
