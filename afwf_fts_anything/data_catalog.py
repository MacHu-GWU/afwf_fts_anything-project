# -*- coding: utf-8 -*-

"""
This module provides DataCatalog, a container that manages multiple Dataset
instances rooted under a single directory, and the DatasetMeta / DatasetMetaStatusEnum
helpers used to describe each discovered dataset's health.
"""

import enum
from dataclasses import dataclass
from pathlib import Path

from .dataset import Dataset
from .setting import Setting


class DatasetMetaStatusEnum(str, enum.Enum):
    """Possible states for a dataset discovered inside a DataCatalog root."""

    setting_not_found = "setting_not_found"
    """The dataset directory exists but contains no ``{name}-setting.json`` file."""

    setting_valid = "setting_valid"
    """The setting file exists and was parsed successfully."""

    setting_invalid = "setting_invalid"
    """The setting file exists but could not be parsed (malformed JSON / schema error)."""


@dataclass
class DatasetMeta:
    """Lightweight descriptor returned by :meth:`DataCatalog.scan`."""

    name: str
    status: DatasetMetaStatusEnum

    @property
    def is_valid(self) -> bool:
        """``True`` only when the setting file is present and well-formed."""
        return self.status == DatasetMetaStatusEnum.setting_valid


@dataclass
class DataCatalog:
    """
    A directory-backed registry of named datasets.

    Expected layout::

        dir_root/
            {dataset_name_1}/
                {dataset_name_1}-setting.json
                {dataset_name_1}-data.json
                {dataset_name_1}-index/
                icons/
            {dataset_name_2}/
                ...

    Each immediate subdirectory of *dir_root* is treated as a potential dataset.
    A subdirectory is included in scan results only when a matching
    ``{name}-setting.json`` file is found inside it.
    """

    dir_root: Path

    def get_dataset(self, name: str) -> Dataset:
        """Return a :class:`.Dataset` for the given *name* rooted at ``dir_root/{name}``."""
        return Dataset(name=name, dir_root=self.dir_root / name)

    def scan(self) -> list[DatasetMeta]:
        """Scan *dir_root* one level deep and return a :class:`DatasetMeta` for each dataset.

        - Subdirectories with no matching setting file are silently skipped.
        - Subdirectories whose setting file cannot be parsed are included with
          status :attr:`~DatasetMetaStatusEnum.setting_invalid`.
        - Results are sorted by dataset name.
        """
        results = []
        for subdir in sorted(self.dir_root.iterdir()):
            if not subdir.is_dir():
                continue  # ignore plain files at the root level

            name = subdir.name
            path_setting = subdir / f"{name}-setting.json"

            if not path_setting.exists():
                continue  # not a dataset directory — skip silently

            try:
                Setting.from_json_file(path_setting)
                status = DatasetMetaStatusEnum.setting_valid
            except Exception:
                status = DatasetMetaStatusEnum.setting_invalid

            results.append(DatasetMeta(name=name, status=status))

        return results
