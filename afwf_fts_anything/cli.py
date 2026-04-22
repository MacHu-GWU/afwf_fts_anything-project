# -*- coding: utf-8 -*-

"""
CLI entry points for the ``afwf-fts-anything`` Alfred workflow.

This module is the wiring layer only: it hard-codes the project-home paths from
:mod:`.paths` and delegates all logic to :mod:`.fts`, :mod:`.data_catalog`, and
:class:`.Dataset`.  :class:`Command` exposes the subcommands via ``fire.Fire``.
"""

import sys
import shutil
from pathlib import Path

import fire
import afwf.api as afwf
import afwf.opt.fuzzy_item.api as fuzzy_item

from .data_catalog import DataCatalog
from .paths import path_enum
from . import fts as fts_mod
from .fts import ActionEnum

_log_error = afwf.log_error(
    log_file=path_enum.path_error_log,
    tb_limit=10,
)


@_log_error
def fts(
    dataset_name: str,
    query: str,
    action: ActionEnum = ActionEnum.open_url,
) -> afwf.ScriptFilter:
    """
    Thin wrapper around :func:`.fts_mod.fts` that supplies the project-home
    paths and wraps the result in a :class:`afwf.ScriptFilter`.

    Query normalisation (bool → empty string) is handled by :meth:`Command.fts`
    before this is called.
    """
    items = fts_mod.fts(
        dataset_name=dataset_name,
        query=query,
        dir_datacatalog_root=path_enum.dir_project_home,
        action=action,
        path_error_log=path_enum.path_error_log,
    )
    return afwf.ScriptFilter(items=items)


@_log_error
def list_datasets_for_reset(
    dataset_name_query: str,
) -> afwf.ScriptFilter:
    """
    Enumerate all valid datasets in the project home and optionally fuzzy-filter
    them.  Each item's action triggers ``rebuild-index`` for that dataset.

    Uses :class:`.DataCatalog` to discover datasets; invalid (unparseable) setting
    files are skipped.  Falls back to the full list when fuzzy matching yields no
    results.
    """
    catalog = DataCatalog(dir_root=path_enum.dir_project_home)
    bin_cli = Path(sys.executable).parent / "afwf-fts-anything"

    items = []
    for meta in catalog.scan():
        if not meta.is_valid:
            # skip datasets whose setting file is malformed
            continue
        dataset = catalog.get_dataset(meta.name)
        setting = dataset.get_setting()
        subtitle = (
            f"data_url: {setting.data_url}"
            if setting.data_url
            else "local data only (no data_url)"
        )
        item = fuzzy_item.Item(title=meta.name, subtitle=subtitle)
        item.set_fuzzy_match_name(meta.name)
        cmd = f"{bin_cli} rebuild-index --dataset-name {meta.name!r}"
        item.run_script(cmd)
        item.send_notification(
            title=f"Rebuilt index: {meta.name!r}",
            subtitle=subtitle,
        )
        items.append(item)

    if not items:
        # no valid datasets found — guide the user to create one
        return afwf.ScriptFilter(
            items=[
                afwf.Item(
                    title="No datasets found",
                    subtitle=f"Add a dataset directory under {path_enum.dir_project_home}",
                    valid=False,
                    icon=afwf.Icon(path=afwf.IconFileEnum.error),
                )
            ]
        )

    if dataset_name_query:
        # user typed something — fuzzy-filter; fall back to full list if no match
        matcher = fuzzy_item.FuzzyItemMatcher.from_items(items)
        matched = matcher.match(dataset_name_query, threshold=0)
        items = matched if matched else items

    return afwf.ScriptFilter(items=items)


@_log_error
def rebuild_index(
    dataset_name: str,
) -> None:
    """
    Destroy and recreate the tantivy index for *dataset_name*.

    Uses :class:`.DataCatalog` to locate the dataset under the project home,
    removes the existing index directory, optionally re-downloads the source
    data, then rebuilds the index.
    """
    catalog = DataCatalog(dir_root=path_enum.dir_project_home)
    dataset = catalog.get_dataset(dataset_name)

    if dataset.dir_index.exists():
        # remove the stale index so build_index starts from scratch
        shutil.rmtree(dataset.dir_index)

    if dataset.setting.data_url:
        # re-download before rebuilding so the index reflects the latest remote data
        dataset.download_data()

    dataset.build_index()


class Command:
    """Alfred workflow subcommands exposed via ``fire.Fire``."""

    def fts(
        self,
        dataset_name: str,
        query: str = "*",
        action: str = ActionEnum.open_url.value,
    ):
        """Full-text search; see :func:`fts`.

        Normalises Fire's boolean ``True`` (blank Alfred field) to an empty
        string before delegating.
        """
        query = "" if isinstance(query, bool) else str(query)
        fts(
            dataset_name=str(dataset_name),
            query=query,
            action=ActionEnum(action),
        ).send_feedback()

    def list_datasets_for_reset(
        self,
        dataset_name_query: str = "",
    ):
        """List datasets with optional fuzzy filter; see :func:`list_datasets_for_reset`.

        Normalises Fire's boolean ``True`` to an empty string before delegating.
        """
        dataset_name_query = "" if isinstance(dataset_name_query, bool) else str(dataset_name_query)
        list_datasets_for_reset(dataset_name_query=dataset_name_query).send_feedback()

    def rebuild_index(
        self,
        dataset_name: str,
    ):
        """Rebuild the search index for a dataset; see :func:`rebuild_index`."""
        rebuild_index(dataset_name=str(dataset_name))


def main():
    fire.Fire(Command)
