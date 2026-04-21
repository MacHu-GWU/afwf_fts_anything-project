# -*- coding: utf-8 -*-

import fire
import afwf.api as afwf

from .dataset import Dataset


@afwf.log_error()
def _fts(dataset_name: str, query: str) -> afwf.ScriptFilter:
    query = str(query)

    if not query:
        return afwf.ScriptFilter(
            items=[
                afwf.Item(
                    title=f"Full text search {dataset_name!r} dataset",
                    subtitle="Please enter a query ...",
                )
            ]
        )

    dataset = Dataset(name=dataset_name)

    if query == "?":
        item = afwf.Item(
            title=f"Open {dataset_name!r} dataset folder location",
            subtitle="hit 'Enter' to open folder location",
            icon=afwf.Icon(path=afwf.IconFileEnum.question),
        )
        item.reveal_file_in_finder(str(dataset._path_setting))
        return afwf.ScriptFilter(items=[item])

    if not dataset._dir_index.exists():
        dataset.build_index()

    doc_list = dataset.search(query)
    setting = dataset.setting
    items = []
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
            if icon.startswith("/"):
                item.set_icon(icon)
            else:
                item.set_icon(str(dataset._dir_icon / icon))
        items.append(item)

    if not items:
        items.append(
            afwf.Item(
                title=f"No result found for query: {query!r}",
                subtitle="hit 'Tab' to enter a new query",
                autocomplete=" ",
                icon=afwf.Icon(path=afwf.IconFileEnum.error),
            )
        )

    return afwf.ScriptFilter(items=items)


class Command:
    def fts(self, dataset_name: str, query: str = ""):
        _fts(dataset_name=str(dataset_name), query=str(query)).send_feedback()


def main():
    fire.Fire(Command)
