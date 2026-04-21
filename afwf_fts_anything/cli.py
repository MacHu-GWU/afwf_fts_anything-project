# -*- coding: utf-8 -*-

import sys
import shutil
from pathlib import Path

import fire
import afwf.api as afwf
import afwf.opt.fuzzy_item.api as fuzzy_item

from .dataset import Dataset
from .paths import path_enum
from .setting import Setting


_log_error = afwf.log_error(
    log_file=path_enum.path_error_log,
    tb_limit=10,
)


@_log_error
def _fts(dataset_name: str, query: str) -> afwf.ScriptFilter:
    query = str(query) if not isinstance(query, bool) else ""

    if not query:
        log_item = afwf.Item(
            title="Open error log",
            subtitle=str(path_enum.path_error_log),
            icon=afwf.Icon(path=afwf.IconFileEnum.error),
        )
        log_item.open_file(str(path_enum.path_error_log))
        return afwf.ScriptFilter(
            items=[
                afwf.Item(
                    title=f"Full text search {dataset_name!r} dataset",
                    subtitle="Please enter a query ...",
                ),
                log_item,
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


@_log_error
def _list_datasets(query: str) -> afwf.ScriptFilter:
    query = str(query) if not isinstance(query, bool) else ""
    project_home = path_enum.dir_project_home
    bin_cli = Path(sys.executable).parent / "afwf-fts-anything"

    items = []
    for setting_file in sorted(project_home.glob("*-setting.json")):
        dataset_name = setting_file.name.removesuffix("-setting.json")
        try:
            setting = Setting.from_json_file(setting_file)
        except Exception:
            continue

        subtitle = (
            f"data_url: {setting.data_url}"
            if setting.data_url
            else "local data only (no data_url)"
        )
        item = fuzzy_item.Item(title=dataset_name, subtitle=subtitle)
        item.set_fuzzy_match_name(dataset_name)

        cmd = f"{bin_cli} rebuild-index --dataset-name {dataset_name!r}"
        item.run_script(cmd)
        item.send_notification(
            title=f"Rebuilt index: {dataset_name!r}",
            subtitle=subtitle,
        )
        items.append(item)

    if not items:
        return afwf.ScriptFilter(
            items=[
                afwf.Item(
                    title="No datasets found",
                    subtitle=f"Put {{name}}-setting.json in {project_home}",
                    valid=False,
                    icon=afwf.Icon(path=afwf.IconFileEnum.error),
                )
            ]
        )

    if query:
        matcher = fuzzy_item.FuzzyItemMatcher.from_items(items)
        matched = matcher.match(query, threshold=0)
        items = matched if matched else items

    return afwf.ScriptFilter(items=items)


@_log_error
def _rebuild_index(dataset_name: str) -> None:
    dataset = Dataset(name=dataset_name)

    if dataset._dir_index.exists():
        shutil.rmtree(dataset._dir_index)

    if dataset.setting.data_url:
        dataset.download_data()

    dataset.build_index()


class Command:
    def fts(self, dataset_name: str, query: str = ""):
        _fts(dataset_name=str(dataset_name), query=str(query)).send_feedback()

    def list_datasets(self, query: str = ""):
        _list_datasets(query=str(query)).send_feedback()

    def rebuild_index(self, dataset_name: str):
        _rebuild_index(dataset_name=str(dataset_name))


def main():
    fire.Fire(Command)
