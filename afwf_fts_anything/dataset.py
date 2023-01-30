# -*- coding: utf-8 -*-

import typing as T

import afwf
import attr
from attrs_mate import AttrsClass
from pathlib_mate import Path

from .paths import dir_project_home


@attr.s
class Dataset(AttrsClass):
    name: str = AttrsClass.ib_str()

    @property
    def path_data(self) -> Path:
        return dir_project_home / f"{self.name}-data.json"

    @property
    def path_setting(self) -> Path:
        return dir_project_home / f"{self.name}-setting.json"

    @property
    def dir_index(self):
        return dir_project_home / f"{self.name}-whoosh_index"
