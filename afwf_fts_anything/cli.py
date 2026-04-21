# -*- coding: utf-8 -*-

"""
CLI entry points for the ``afwf-fts-anything`` Alfred workflow.

Implementations live in :func:`_fts`, :func:`_list_datasets`, and
:func:`_rebuild_index`.  :class:`Command` wraps them for ``fire.Fire``.
"""

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
    """
    Core implementation of the ``fts`` subcommand — full-text search over a
    named dataset.  Called on every keystroke by the Alfred Script Filter.

    **Query normalisation**

    Alfred passes the user's input via ``--query {query}`` (no quotes around
    ``{query}``).  Alfred backslash-escapes spaces so the shell treats the
    string as a single argument.  Two edge cases require explicit handling:

    - *Empty input* — when the Alfred field is blank, ``{query}`` expands to
      nothing and the shell command becomes bare ``--query`` with no value.
      Python Fire then assigns the boolean ``True`` to the parameter instead
      of an empty string.  The first line therefore converts any ``bool``
      value to ``""`` so the empty-query branch fires correctly::

          query = str(query) if not isinstance(query, bool) else ""

    - *Do not quote* ``{query}`` in the Alfred Script Filter command.
      Single quotes pass backslashes through literally, so
      ``--query '{query}'`` would deliver ``god\\ father`` to the process
      instead of ``god father``.

    **Branches**

    - ``query == ""`` — prompt screen: shows a "please type a query" hint
      and an "Open error log" shortcut (see *Error handling* below).
    - ``query == "?"`` — reveal the dataset's setting file in Finder.
    - Otherwise — build the index on first run if absent, search, and return
      result items.  Falls back to a "No result found" item when the index
      returns no hits.

    **Error handling and logging**

    Decorated with the module-level ``_log_error`` instance
    (:func:`afwf.log_error` configured with
    ``log_file=path_enum.path_error_log, tb_limit=10``).  On any unhandled
    exception the full traceback (up to 10 frames) is appended to
    ``~/.alfred-afwf/afwf_fts_anything/error.log`` before the exception is
    re-raised.  The log file rotates at ~500 KB, keeping 2 backups.

    To access the log without leaving Alfred: clear the search field to reach
    the prompt screen, then press Enter on the "Open error log" item.  That
    item carries an :meth:`afwf.Item.open_file` action pointing at
    :attr:`.PathEnum.path_error_log`.
    """
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
    """
    Core implementation of the ``list-datasets`` subcommand — enumerate all
    configured datasets and optionally fuzzy-filter them.

    **How it works**

    Scans :attr:`.PathEnum.dir_project_home` for ``*-setting.json`` files.
    Each valid file becomes one :class:`fuzzy_item.Item` whose ``arg`` runs
    ``afwf-fts-anything rebuild-index --dataset-name <name>`` and sends a
    macOS notification on completion.  Files that fail JSON parsing are
    silently skipped so a broken config cannot prevent the rest from showing.

    When ``query`` is non-empty the results are passed through
    :class:`fuzzy_item.FuzzyItemMatcher`; if nothing matches, the full list
    is returned unchanged so the user always sees something.

    **Query normalisation**

    Same bool-guard as :func:`_fts`: a bare ``--query`` with no value is
    delivered by Fire as ``True``; this is converted to ``""`` so the
    unfiltered list is shown rather than a spurious fuzzy search for
    ``"True"``.

    **Error handling**

    Decorated with the shared ``_log_error`` instance; exceptions are logged
    to :attr:`.PathEnum.path_error_log` with a 10-frame traceback limit.
    """
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
    """
    Core implementation of the ``rebuild-index`` subcommand — destroy and
    recreate the tantivy search index for a dataset.

    **How it works**

    Removes the existing index directory if present, optionally re-downloads
    the source data when :attr:`.Setting.data_url` is set, then calls
    :meth:`.Dataset.build_index` to create a fresh index.  Intended to be
    invoked from an Alfred Run Script action after the user selects a dataset
    in the :func:`_list_datasets` screen.

    **Error handling**

    Decorated with the shared ``_log_error`` instance; exceptions are logged
    to :attr:`.PathEnum.path_error_log` with a 10-frame traceback limit.
    """
    dataset = Dataset(name=dataset_name)

    if dataset._dir_index.exists():
        shutil.rmtree(dataset._dir_index)

    if dataset.setting.data_url:
        dataset.download_data()

    dataset.build_index()


class Command:
    """Alfred workflow subcommands exposed via ``fire.Fire``."""

    def fts(self, dataset_name: str, query: str = ""):
        """Full-text search; see :func:`_fts`."""
        _fts(dataset_name=str(dataset_name), query=str(query)).send_feedback()

    def list_datasets(self, query: str = ""):
        """List datasets with optional fuzzy filter; see :func:`_list_datasets`."""
        _list_datasets(query=str(query)).send_feedback()

    def rebuild_index(self, dataset_name: str):
        """Rebuild the search index for a dataset; see :func:`_rebuild_index`."""
        _rebuild_index(dataset_name=str(dataset_name))


def main():
    fire.Fire(Command)
