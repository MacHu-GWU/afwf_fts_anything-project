# -*- coding: utf-8 -*-

import attr
import shutil
from attrs_mate import AttrsClass
from whoosh import index, qparser
from pathlib_mate import PathCls as Path
from superjson import json
from .constant import ALFRED_FTS
from .fts_setting import Setting


@attr.s
class DataSet(AttrsClass):
    """
    Represent the dataset you want to search.

    :param data: dict list.
    :param columns: list.

    :param title_field: str, the field used for alfred workflow item title.
    :param subtitle_field: str, the field used for alfred workflow item subtitle.
    :param arg_field: str, the field used for alfred workflow item argument.
    :param autocomplete_field: str, the field used for alfred workflow item autocomplete.
    """
    name = attr.ib(default=None)
    data = attr.ib(default=None)
    setting = attr.ib(
        converter=Setting.from_dict,
        validator=attr.validators.optional(
            attr.validators.instance_of(Setting),
        ),
        factory=Setting,
    )
    schema_cache = attr.ib(default=None)

    def update_data_from_file(self):
        if self.data is None:
            data_file = self.get_data_file_path()
            with open(data_file.abspath, "rb") as f:
                self.data = json.loads(f.read().decode(
                    "utf-8"), ignore_comments=True)

    def update_setting_from_file(self):
        if not self.setting.columns:
            setting_file = self.get_setting_file_path()
            with open(setting_file.abspath, "rb") as f:
                setting_data = json.loads(
                    f.read().decode("utf-8"), ignore_comments=True)
                self.setting = Setting(**setting_data)

    def get_data_file_path(self):
        return Path(ALFRED_FTS, "{}.json".format(self.name))

    def get_setting_file_path(self):
        return Path(ALFRED_FTS, "{}-setting.json".format(self.name))

    def get_index_dir_path(self):
        return Path(ALFRED_FTS, "{}-whoosh_index".format(self.name))

    def get_schema(self):
        if self.schema_cache is None:
            self.schema_cache = self.setting.create_whoosh_schema()
        return self.schema_cache

    def get_index(self):
        index_dir = self.get_index_dir_path()
        if index_dir.exists():
            idx = index.open_dir(index_dir.abspath)
        else:
            schema = self.get_schema()
            index_dir.mkdir()
            idx = index.create_in(dirname=index_dir.abspath, schema=schema)
        return idx

    def build_index(self, idx):
        """
        Build Whoosh Index, add document.
        """
        self.update_data_from_file()
        writer = idx.writer()
        for row in self.data:
            doc = {c.name: row.get(c.name) for c in self.setting.columns}
            writer.add_document(**doc)
        writer.commit()

    def remove_index(self):
        """
        Remove whoosh index dir.
        """
        shutil.rmtree(self.get_index_dir_path().abspath)

    def search(self, query_str, limit=20):
        """
        Use full text search for result.
        """
        schema = self.get_schema()
        idx = self.get_index()
        query = qparser.MultifieldParser(
            self.setting.searchable_columns,
            schema=schema,
        ).parse(query_str)
        with idx.searcher() as searcher:
            result = [hit.fields()
                      for hit in searcher.search(query, limit=limit)]
        return result
