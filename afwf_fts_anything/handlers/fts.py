# -*- coding: utf-8 -*-

import typing as T
import afwf
import attr
from pathlib_mate import Path

from ..dataset import Dataset


@attr.define
class Handler(afwf.Handler):
    def main(
        self,
        dataset_name: str,
        query_str: str,
        path_setting: T.Optional[Path] = None,
        path_data: T.Optional[Path] = None,
        dir_index: T.Optional[Path] = None,
    ) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()

        kwargs = dict(
            name=dataset_name,
            path_setting=path_setting,
            path_data=path_data,
            dir_index=dir_index,
        )
        cleaned_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        dataset = Dataset(**cleaned_kwargs)
        doc_list = dataset.search(query_str)
        setting = dataset.setting
        for doc in doc_list:
            item = afwf.Item(
                title=setting.format_title(doc),
                subtitle=setting.format_subtitle(doc),
                arg=setting.format_arg(doc),
                autocomplete=setting.format_autocomplete(doc),
            )
            icon = setting.format_icon(doc)
            if icon is not None:
                # use absolute path
                if icon.startswith("/"):
                    item.set_icon(icon)
                # use relative path
                else:
                    item.set_icon(dataset._dir_icon.joinpath(icon).abspath)
            sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        dataset_name, query_str = query.split(" ", 1)
        return dict(
            dataset_name=dataset_name,
            query_str=query_str,
        )


handler = Handler(id="fts")
