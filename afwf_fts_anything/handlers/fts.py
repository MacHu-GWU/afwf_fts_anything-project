# -*- coding: utf-8 -*-

import typing as T
import afwf
import attr
from pathlib_mate import Path

from ..dataset import Dataset
from ..exc import GetDataError, BuildIndexError


@attr.define
class Handler(afwf.Handler):
    def build_index(self, dataset: Dataset):
        """
        Build whoosh index if not exists.
        """
        # if index already exists skip it
        if dataset._dir_index.exists() is False:
            # try to build index, if anything wrong, clear the whoosh index
            try:
                data = dataset.get_data()
            except Exception as e: # pragma: no cover
                raise GetDataError(f"GetDataError, {e}")
            try:
                dataset.build_index(data)
            except Exception as e: # pragma: no cover
                dataset._dir_index.remove_if_exists()
                raise BuildIndexError(f"BuildIndexError, {e}")

    def main(
        self,
        dataset_name: str,
        query_str: str,
        path_setting: T.Optional[Path] = None,
        path_data: T.Optional[Path] = None,
        dir_index: T.Optional[Path] = None,
    ) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()

        # prompt
        if len(query_str) == 0:
            item = afwf.Item(
                title=f"Full text search {dataset_name!r} dataset",
                subtitle=f"Please enter a query ...",
            )
            sf.items.append(item)
            return sf

        kwargs = dict(
            name=dataset_name,
            path_setting=path_setting,
            path_data=path_data,
            dir_index=dir_index,
        )
        cleaned_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        dataset = Dataset(**cleaned_kwargs)

        if query_str == "?":
            item = afwf.Item(
                title=f"Open {dataset_name!r} dataset folder location",
                subtitle=f"hit 'Enter' to open folder location",
            )
            item.set_icon(afwf.IconFileEnum.question)
            item.reveal_file_in_finder(dataset._path_setting.abspath)
            sf.items.append(item)
            return sf

        self.build_index(dataset)

        # happy path
        doc_list = dataset.search(query_str)
        setting = dataset.setting
        for doc in doc_list:
            arg = setting.format_arg(doc)
            item = afwf.Item(
                title=setting.format_title(doc),
                subtitle=setting.format_subtitle(doc),
                arg=arg,
                autocomplete=setting.format_autocomplete(doc),
            )
            item.open_url(url=arg)
            icon = setting.format_icon(doc)
            if icon is not None:
                # use absolute path
                if icon.startswith("/"):
                    item.set_icon(icon)
                # use relative path
                else:
                    item.set_icon(dataset._dir_icon.joinpath(icon).abspath)
            sf.items.append(item)

        # found no result
        if len(sf.items) == 0:
            item = afwf.Item(
                title=f"No result found for query: {query_str!r}",
                subtitle="hit 'Tab' to enter a new query",
                autocomplete=" ",
            )
            item.set_icon(afwf.IconFileEnum.error)
            sf.items.append(item)

        return sf

    def parse_query(self, query: str):
        afwf.log_debug_info(f"receive query: {query!r}")
        # strip all delimiter except ?, because ? is used for special action
        q = afwf.QueryParser(delimiter=list(" ~`!@#$%^&*()-_=+{}[]\\|:;\"'<>,./")).parse(query)
        afwf.log_debug_info(f"trimmed parts: {q.trimmed_parts}")
        dataset_name = q.trimmed_parts[0]
        query_str = " ".join(q.trimmed_parts[1:])
        return dict(
            dataset_name=dataset_name,
            query_str=query_str,
        )


handler = Handler(id="fts")
