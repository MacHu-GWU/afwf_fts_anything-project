# -*- coding: utf-8 -*-

import attr
from attrs_mate import AttrsClass
from pathlib_mate import Path

from .paths import dir_project_home


@attr.s
class Dataset(AttrsClass):
    """
    A Dataset is a search scope of your full-text-search application.

    It has to have a unique name, which is used in the Alfred Workflow script filter
    command to locate the setting and the data.

    It has to have three files in the project home directory ``${HOME}/.alfred-afwf/afwf_fts_anything/``:

    - ``${name}-setting.json``: the setting file, which contains the search setting of this dataset.
    - ``${name}-data.json``: the data file, which contains the data you want to search.
        this file can be user generated, or downloaded from the internet
    - ``${name}-whoosh_index``: the index directory, which contains the whoosh index of this dataset.
        the folder is automatically generated based on your setting and data.
    """
    name: str = AttrsClass.ib_str()

    @property
    def path_setting(self) -> Path:
        return dir_project_home / f"{self.name}-setting.json"

    @property
    def path_data(self) -> Path:
        return dir_project_home / f"{self.name}-data.json"

    @property
    def dir_index(self) -> Path:
        return dir_project_home / f"{self.name}-whoosh_index"
