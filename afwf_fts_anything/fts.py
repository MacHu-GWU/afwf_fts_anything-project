# -*- coding: utf-8 -*-

"""
Pure-logic implementation of the full-text-search Alfred action.

:func:`fts` is dependency-injected (no global ``path_enum`` references) so it
can be unit-tested in isolation.  ``cli.py`` is responsible for wiring real
paths and sending feedback to Alfred.
"""

import enum
from pathlib import Path

import afwf.api as afwf

from .data_catalog import DataCatalog


class ActionEnum(str, enum.Enum):
    """Alfred action triggered when the user presses Enter on a search result."""

    open_url = "open_url"
    """Pass *arg* to :meth:`afwf.Item.open_url` — suitable for URL-valued args."""

    open_file = "open_file"
    """Pass *arg* to :meth:`afwf.Item.open_file` — suitable for file-path args."""


def fts(
    dataset_name: str,
    query: str,
    dir_datacatalog_root: Path,
    action: ActionEnum = ActionEnum.open_url,
    path_error_log: Path | None = None,
) -> list[afwf.Item]:
    """
    Core full-text-search logic for the ``fts`` Alfred Script Filter.

    :param dataset_name: name of the dataset to search.
    :param query: user's raw query string (already normalised by the caller —
        never a ``bool``).
    :param dir_datacatalog_root: root directory of the :class:`.DataCatalog`;
        the dataset lives at ``{dir_datacatalog_root}/{dataset_name}/``.
    :param action: Alfred action bound to each result item; defaults to
        :attr:`ActionEnum.open_url`.
    :param path_error_log: when provided and *query* is empty, an
        "Open error log" item is appended so the user can access it from Alfred.

    **Branches**

    - ``query == "?"`` — reveal the dataset's setting file in Finder; returns
      immediately without touching the index.
    - Otherwise — build the index on first run if absent, then search.
      An empty query is translated to ``"*"`` (tantivy all-documents wildcard).
      Falls back to a "No result found" item when the index returns no hits for
      a non-empty query.  Appends the error-log item when *query* is empty and
      *path_error_log* is given.
    """
    catalog = DataCatalog(dir_root=dir_datacatalog_root)
    dataset = catalog.get_dataset(dataset_name)

    if not dataset.path_setting.exists():
        item = afwf.Item(
            title=f"Setting file not found for dataset {dataset_name!r}",
            subtitle=str(dataset.path_setting),
            arg=str(dataset.path_setting),
            icon=afwf.Icon(path=afwf.IconFileEnum.error),
        )
        item.open_file(str(dataset.path_setting))
        return [item]

    if query == "?":
        # special "?" query: reveal the dataset's setting file in Finder instead of searching
        item = afwf.Item(
            title=f"Open {dataset_name!r} dataset folder location",
            subtitle="hit 'Enter' to open folder location",
            icon=afwf.Icon(path=afwf.IconFileEnum.question),
        )
        item.reveal_file_in_finder(str(dataset.path_setting))
        return [item]

    # normal search path: build the index on first run if it doesn't exist yet
    if not dataset.dir_index.exists():
        try:
            dataset.build_index()
        except Exception as e:
            item = afwf.Item(
                title=f"Failed to build index for dataset {dataset_name!r}: {type(e).__name__}",
                subtitle=str(e),
                arg=str(dataset.path_setting),
                icon=afwf.Icon(path=afwf.IconFileEnum.error),
            )
            item.open_file(str(dataset.path_setting))
            return [item]

    try:
        doc_list = dataset.search(query or "*")  # empty query → "*" to return all docs
    except Exception as e:
        item = afwf.Item(
            title=f"Search failed for dataset {dataset_name!r}: {type(e).__name__}",
            subtitle=str(e),
            arg=str(dataset.path_setting),
            icon=afwf.Icon(path=afwf.IconFileEnum.error),
        )
        item.open_file(str(dataset.path_setting))
        return [item]
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
        if arg is not None:
            if action is ActionEnum.open_url:
                item.open_url(url=arg)
            elif action is ActionEnum.open_file:
                item.open_file(arg)
            else:
                raise TypeError(f"Unsupported action: {action!r}")
        icon = setting.format_icon(doc)
        if icon is not None:
            if icon.startswith("/"):
                # absolute path — use as-is
                item.set_icon(icon)
            else:
                # relative filename — resolve against the dataset's icons directory
                item.set_icon(str(dataset.dir_root / "icons" / icon))
        items.append(item)

    if not items and query:
        # non-empty query produced no hits — show a placeholder instead of blank results
        items.append(
            afwf.Item(
                title=f"No result found for query: {query!r}",
                subtitle="hit 'Tab' to enter a new query",
                autocomplete=" ",
                icon=afwf.Icon(path=afwf.IconFileEnum.error),
            )
        )

    if not query and path_error_log is not None:
        # empty query (first open) — append the error-log shortcut at the bottom
        log_item = afwf.Item(
            title="Open error log",
            subtitle=str(path_error_log),
            icon=afwf.Icon(path=afwf.IconFileEnum.error),
        )
        log_item.open_file(str(path_error_log))
        items.append(log_item)

    return items
