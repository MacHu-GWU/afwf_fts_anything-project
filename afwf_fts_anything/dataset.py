# -*- coding: utf-8 -*-

"""
This module implements the Dataset class, which binds a Setting to a sayt2
search index and provides build/search operations.
"""

import io
import json
import typing as T
import urllib.request
from pathlib import Path
from zipfile import ZipFile
from dataclasses import dataclass
from functools import cached_property

from sayt2.api import DataSet as Sayt2DataSet

from .setting import Setting


@dataclass
class Dataset:
    """
    A search dataset backed by a sayt2 index.

    Identified by a *name* and a *dir_root* directory that owns all dataset
    resources under a shared convention:

    - ``{dir_root}/{name}-setting.json`` -- field schema and display config
    - ``{dir_root}/{name}-data.json``    -- the records to index
    - ``{dir_root}/{name}-index/``       -- sayt2 index directory (auto-created)
    - ``{dir_root}/icons/{name}.png``    -- per-result icons (resolved on demand)
    """

    name: str
    dir_root: Path

    # ------------------------------------------------------------------
    # Computed paths (cached so repeated access is free)
    # ------------------------------------------------------------------

    @cached_property
    def path_setting(self) -> Path:
        return self.dir_root / f"{self.name}-setting.json"

    @cached_property
    def path_data(self) -> Path:
        return self.dir_root / f"{self.name}-data.json"

    @cached_property
    def dir_index(self) -> Path:
        return self.dir_root / f"{self.name}-index"

    @cached_property
    def dir_icons(self) -> Path:
        return self.dir_root / "icons"

    # ------------------------------------------------------------------
    # Resource accessors
    # ------------------------------------------------------------------

    def get_icon(self, name: str) -> Path:
        """Return the path to ``{dir_icons}/{name}``."""
        return self.dir_icons / name

    def get_setting(self) -> Setting:
        """Load and return the :class:`.Setting` from disk (no cache)."""
        return Setting.from_json_file(self.path_setting)

    def get_data(self) -> list[dict]:
        """Read records from the local data JSON file.

        If the file does not exist, :meth:`download_data` is called first.
        """
        if not self.path_data.exists():  # pragma: no cover
            self.download_data()
        return json.loads(self.path_data.read_text())

    @cached_property
    def setting(self) -> Setting:
        """Parsed :class:`.Setting`, cached after the first call."""
        return self.get_setting()

    def get_sayt2_dataset(self) -> Sayt2DataSet:
        """Create a :class:`sayt2.DataSet` wired to this dataset's index and setting."""
        return Sayt2DataSet(
            dir_root=self.dir_index,
            name=self.name,
            fields=self.setting.fields,
            downloader=self.get_data,
            sort=self.setting.sort,
        )

    # ------------------------------------------------------------------
    # Download helpers (network-free parts are testable)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json_from_zip(zip_bytes: bytes) -> bytes:
        """Return the raw bytes of the first ``.json`` file found in *zip_bytes*."""
        with ZipFile(io.BytesIO(zip_bytes)) as zf:
            json_names = [n for n in zf.namelist() if n.endswith(".json")]
            return zf.read(json_names[0])

    def _save_data(self, raw_bytes: bytes, is_zip: bool) -> None:
        """Write *raw_bytes* to :attr:`path_data`, decompressing if *is_zip* is True."""
        data_bytes = self._extract_json_from_zip(raw_bytes) if is_zip else raw_bytes
        self.path_data.write_bytes(data_bytes)

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
                f"'data_url' is not defined in setting file '{self.path_setting}'."
            )
        raw = self._fetch_url(url)
        self._save_data(raw, is_zip=url.endswith(".zip"))

    # ------------------------------------------------------------------
    # Index and search
    # ------------------------------------------------------------------

    def build_index(
        self,
        data: list[dict[str, T.Any]] | None = None,
        rebuild: bool = False,
    ) -> int:
        """Build the sayt2 search index from *data*.

        :param data: records to index; if ``None`` the configured downloader is used.
        :param rebuild: if ``True``, evict the query cache before building so
            subsequent searches always reflect the new index.
        :returns: number of documents indexed.
        """
        ds = self.get_sayt2_dataset()
        if rebuild:
            ds._cache.evict_all()
        count = ds.build_index(data=data)
        ds.close()
        return count

    def search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict[str, T.Any]]:
        """Search the index and return matching documents as plain dicts.

        :param query: Lucene-syntax query string.
        :param limit: maximum number of results to return.
        :returns: list of ``hit.source`` dicts ordered by relevance / sort key.
        """
        with self.get_sayt2_dataset() as ds:
            result = ds.search(query, limit=limit)
        return [hit.source for hit in result.hits]
