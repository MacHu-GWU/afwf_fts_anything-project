# -*- coding: utf-8 -*-

import typing as T
import os
import json
from zipfile import ZipFile

import attr
from attrs_mate import AttrsClass
from pathlib_mate import Path
import requests
from whoosh import fields, qparser, query, sorting
from whoosh.index import open_dir, create_in, FileIndex

from .paths import dir_project_home, dir_cache
from .compat import cached_property
from .cache import cache
from .setting import Setting


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
    - ``${name}-icon``: the icon directory, which contains the icon for Alfred.
    """

    name: str = AttrsClass.ib_str()
    path_setting: T.Optional[Path] = AttrsClass.ib_generic(
        type_=Path, nullable=True, default=None
    )
    path_data: T.Optional[Path] = AttrsClass.ib_generic(
        type_=Path, nullable=True, default=None
    )
    dir_index: T.Optional[Path] = AttrsClass.ib_generic(
        type_=Path, nullable=True, default=None
    )
    dir_icon: T.Optional[Path] = AttrsClass.ib_generic(
        type_=Path, nullable=True, default=None
    )

    @property
    def _path_setting(self) -> Path:
        """
        The path to the setting file.
        """
        if self.path_setting is not None:
            return self.path_setting
        return dir_project_home / f"{self.name}-setting.json"

    @property
    def _path_data(self) -> Path:
        """
        The path to the data file.
        """
        if self.path_data is not None:
            return self.path_data
        return dir_project_home / f"{self.name}-data.json"

    @property
    def _dir_index(self) -> Path:
        """
        The path to the whoosh index directory.
        """
        if self.dir_index is not None:
            return self.dir_index
        return dir_project_home / f"{self.name}-whoosh_index"

    @property
    def _dir_icon(self) -> Path:
        """
        The path to the icon directory.
        """
        if self.dir_icon is not None:
            return self.dir_icon
        return dir_project_home / f"{self.name}-icon"

    @cached_property
    def setting(self) -> Setting:
        """
        Access the setting object that is parsed from the setting file.
        """
        return Setting.from_json_file(self._path_setting)

    @cached_property
    def schema(self) -> fields.Schema:
        """
        Access the whoosh schema based on the setting.
        """
        return self.setting.create_whoosh_schema()

    def download_data(self): # pragma: no cover
        """
        Download the data from the internet if
        """
        if self.setting.data_url is None:
            raise ValueError(
                "You cannot download data because 'data_url' "
                f"is not defined in the setting file '{self._path_setting}'."
            )
        response = requests.get(self.setting.data_url)

        # write to temp file first, then move to the data file for atomic write
        if self.setting.data_url.endswith(".zip"):
            # download to *.temp.zip first
            path_temp = Path(str(self._path_data) + ".temp.zip")
            path_temp.write_bytes(response.content)
            # unzip to tmp/ folder
            dir_temp = path_temp.change(new_basename="tmp")
            dir_temp.mkdir_if_not_exists()
            with ZipFile(path_temp.abspath, "r") as zf:
                zf.extractall(dir_temp.abspath)
            # move the data file to the right location
            for path in dir_temp.select_by_ext(".json"):
                path.moveto(
                    new_abspath=path_temp.parent.joinpath(path.relative_to(dir_temp)).abspath,
                    overwrite=True
                )
            # delete the tmp/ folder
            dir_temp.remove_if_exists()
        else:
            path_temp = Path(str(self._path_data) + ".temp")
            path_temp.write_text(response.text)
            path_temp.moveto(new_abspath=self._path_data, overwrite=True)


    def get_data(self) -> T.List[T.Dict[str, T.Any]]:
        """
        Get the data from the data file. If data file does not exist, download it first.
        """
        if not self._path_data.exists(): # pragma: no cover
            self.download_data()
        return json.loads(self._path_data.read_text())

    def get_index(self) -> FileIndex:
        if self._dir_index.exists():
            idx = open_dir(self._dir_index.abspath)
        else:
            self._dir_index.mkdir(parents=True, exist_ok=True)
            idx = create_in(dirname=self._dir_index.abspath, schema=self.schema)
        return idx

    def remove_index(self):
        """
        Remove the whoosh index diretory.
        """
        self._dir_index.remove_if_exists()

    def build_index(
        self,
        data: T.List[T.Dict[str, T.Any]],
        multi_thread: bool = False,
        rebuild: bool = False,
    ):
        if rebuild is True:
            self.remove_index()
        idx = self.get_index()
        if multi_thread:  # pragma: no cover
            writer = idx.writer(procs=os.cpu_count())
        else:
            writer = idx.writer()

        for row in data:
            doc = {
                field_name: row.get(field_name)
                for field_name in self.setting.field_names
            }
            writer.add_document(**doc)
        writer.commit()

    def clear_cache(self): # pragma: no cover
        dir_cache.remove_if_exists()

    @cache.memoize(expire=5)
    def search(self, query_str, limit=20) -> T.List[dict]:
        """
        Use full-text search for result.
        """
        idx = self.get_index()
        q = query.And(
            [
                qparser.MultifieldParser(
                    self.setting.searchable_fields,
                    schema=self.schema,
                ).parse(query_str),
            ]
        )
        multi_facet = sorting.MultiFacet()
        for field_name in self.setting.sortable_fields:
            field = self.setting.fields_mapper[field_name]
            multi_facet.add_field(field_name, reverse=not field.is_sort_ascending)
        with idx.searcher() as searcher:
            doc_list = [
                hit.fields()
                for hit in searcher.search(
                    q,
                    sortedby=multi_facet,
                    limit=limit,
                )
            ]
        return doc_list
