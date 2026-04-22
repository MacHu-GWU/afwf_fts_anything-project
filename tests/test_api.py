# -*- coding: utf-8 -*-

from afwf_fts_anything import api


def test():
    _ = api

    _ = api.BuildIndexError
    _ = api.GetDataError
    _ = api.MalformedSettingError
    _ = api.Setting
    _ = api.Dataset
    _ = api.DataCatalog
    _ = api.DatasetMeta
    _ = api.DatasetMetaStatusEnum
    _ = api.fts


if __name__ == "__main__":
    from afwf_fts_anything.tests import run_cov_test

    run_cov_test(
        __file__,
        "afwf_fts_anything.api",
        preview=False,
    )
