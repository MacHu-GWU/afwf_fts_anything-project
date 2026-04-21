# -*- coding: utf-8 -*-

"""
This module implements the Dataset class, which binds a Setting to a sayt2
search index and provides build/search operations.
"""

import io
import json
import urllib.request
from pathlib import Path
from zipfile import ZipFile
from functools import cached_property

from sayt2.api import DataSet as Sayt2DataSet

from .paths import path_enum
from .setting import Setting


class Dataset:
    """
    A search dataset backed by a sayt2 index.

    It is identified by a unique *name* and expects three resources in the
    project-home directory (``~/.alfred-afwf/afwf_fts_anything/``):

    - ``{name}-setting.json`` -- field schema and display config
    - ``{name}-data.json`` -- the records to index
    - ``{name}-index/`` -- the sayt2 index directory (auto-created)

    All four path arguments are optional overrides for testing or non-standard
    layouts.
    """

    def __init__(
        self,
        name: str,
        path_setting: Path | None = None,
        path_data: Path | None = None,
        dir_index: Path | None = None,
        dir_icon: Path | None = None,
    ):
        self.name = name
        self.path_setting = path_setting
        self.path_data = path_data
        self.dir_index = dir_index
        self.dir_icon = dir_icon

    # ------------------------------------------------------------------
    # Resolved paths
    # ------------------------------------------------------------------

    @property
    def _path_setting(self) -> Path:
        """Resolved path to the setting JSON file."""
        return (
            self.path_setting
            or path_enum.dir_project_home / f"{self.name}-setting.json"
        )

    @property
    def _path_data(self) -> Path:
        """Resolved path to the data JSON file."""
        return self.path_data or path_enum.dir_project_home / f"{self.name}-data.json"

    @property
    def _dir_index(self) -> Path:
        """Resolved path to the sayt2 index directory."""
        return self.dir_index or path_enum.dir_project_home / f"{self.name}-index"

    @property
    def _dir_icon(self) -> Path:
        """Resolved path to the icon directory."""
        return self.dir_icon or path_enum.dir_project_home / f"{self.name}-icon"

    # ------------------------------------------------------------------
    # Setting
    # ------------------------------------------------------------------

    @cached_property
    def setting(self) -> Setting:
        """Parsed :class:`.Setting` loaded from :attr:`_path_setting`."""
        return Setting.from_json_file(self._path_setting)

    # ------------------------------------------------------------------
    # sayt2 DataSet factory
    # ------------------------------------------------------------------

    def _make_sayt2_dataset(self) -> Sayt2DataSet:
        """Create a :class:`sayt2.DataSet` wired to this dataset's index and setting."""
        return Sayt2DataSet(
            dir_root=self._dir_index,
            name=self.name,
            fields=self.setting.fields,
            downloader=self.get_data,
            sort=self.setting.sort,
        )

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def get_data(self) -> list[dict]:
        """Read records from the local data JSON file.

        If the file does not exist, :meth:`download_data` is called first.
        """
        if not self._path_data.exists():  # pragma: no cover
            self.download_data()
        return json.loads(self._path_data.read_text())

    # ------------------------------------------------------------------
    # Download helpers (network-free parts are testable)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json_from_zip(zip_bytes: bytes) -> bytes:
        """Return the raw bytes of the first ``.json`` file found in *zip_bytes*."""
        with ZipFile(io.BytesIO(zip_bytes)) as zf:
            json_names = [n for n in zf.namelist() if n.endswith(".json")]
            return zf.read(json_names[0])

    def _save_data(
        self,
        raw_bytes: bytes,
        is_zip: bool,
    ) -> None:
        """Write *raw_bytes* to :attr:`_path_data`, decompressing if *is_zip* is True."""
        data_bytes = self._extract_json_from_zip(raw_bytes) if is_zip else raw_bytes
        self._path_data.write_bytes(data_bytes)

    def _fetch_url(self, url: str) -> bytes:  # pragma: no cover
        """Download *url* and return raw bytes via :mod:`urllib`."""
        with urllib.request.urlopen(url) as resp:
            return resp.read()

    def download_data(self) -> None:  # pragma: no cover
        """Download the dataset from :attr:`Setting.data_url` and save it locally.

        Raises :class:`ValueError` if ``data_url`` is not configured.
        """
        url = self.setting.data_url
        if url is None:
            raise ValueError(
                f"'data_url' is not defined in setting file '{self._path_setting}'."
            )
        raw = self._fetch_url(url)
        self._save_data(raw, is_zip=url.endswith(".zip"))

    # ------------------------------------------------------------------
    # Index and search
    # ------------------------------------------------------------------

    def build_index(
        self,
        data: list[dict] | None = None,
        rebuild: bool = False,
    ) -> int:
        """Build the sayt2 search index from *data*.

        :param data: records to index; if ``None`` the configured downloader is used.
        :param rebuild: if ``True``, evict the query cache before building so
            subsequent searches always reflect the new index.
        :returns: number of documents indexed.
        """
        ds = self._make_sayt2_dataset()
        if rebuild:
            ds._cache.evict_all()
        count = ds.build_index(data=data)
        ds.close()
        return count

    def search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict]:
        """Search the index and return matching documents as plain dicts.

        :param query: Lucene-syntax query string.
        :param limit: maximum number of results to return.
        :returns: list of ``hit.source`` dicts ordered by relevance / sort key.
        """
        with self._make_sayt2_dataset() as ds:
            result = ds.search(query, limit=limit)
        return [hit.source for hit in result.hits]
