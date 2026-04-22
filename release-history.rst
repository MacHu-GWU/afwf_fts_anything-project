.. _release_history:

Release and Version History
==============================================================================


Backlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


2.0.1 (2026-04-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Replaced the ``whoosh`` search backend with ``sayt2``, delivering faster indexing and more robust full-text search.
- Introduced ``DataCatalog`` — a directory-backed registry that discovers and manages multiple named datasets under a single root directory.
- Added ``ActionEnum`` (``open_url`` / ``open_file``) so each dataset can specify whether pressing Enter opens a URL or a local file path.
- Added ``setup-sample-data`` CLI command that copies the bundled movie dataset into the workflow home, enabling a zero-configuration quick-start experience.
- Added ``list-datasets-for-reset`` CLI command that lists all valid datasets with fuzzy filtering so users can rebuild a specific dataset index directly from Alfred.
- Added ``rebuild-index`` CLI command to destroy and recreate the search index for a dataset, with optional re-download when ``data_url`` is configured.
- The ``?`` query now reveals the dataset's setting file in Finder instead of returning search results.

**Breaking Changes**

- ``Dataset`` is now a ``dataclass`` with a ``dir_root`` parameter; the old ``path_setting`` / ``path_data`` / ``dir_index`` / ``dir_icon`` attribute overrides are removed. Each dataset is expected to live under its own subdirectory (``{root}/{name}/``).
- ``Setting`` has been rewritten using Pydantic and ``sayt2`` field types; the old ``whoosh``-based schema helpers (``create_whoosh_schema``, ``searchable_fields``, ``sortable_fields``) are gone.
- Removed the ``diskcache``-based ``cache.py`` module and the global ``cache`` object; query caching is now handled internally by ``sayt2``.
- Removed ``compat.py``; ``functools.cached_property`` (Python 3.8+) is used directly.
- Removed the ``requests`` dependency; data downloads now use the standard library ``urllib``.

**Miscellaneous**

- Migrated build and dependency management from ``poetry`` to ``uv``.
- Bundled the movie sample dataset inside the package (``afwf_fts_anything/tests/data/movie/``) so it is always available without a network call.
- Restructured documentation into topic-based pages covering quick-start, data catalog, setting/data files, Alfred workflow setup, and building custom datasets.


1.2.1 (2024-01-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``ngram_words`` index type. It tokenizes the text into words before index. It is more accurate than ``ngram`` if you have delimiter in your text.

**Minor Improvements**

- Fix a bug that it also open the url even it is not a valid url item.


1.1.1 (2023-04-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First API stable release.
- drop support for Python2.7.
- only support for Python3.7+.
- adapt `afwf <https://github.com/MacHu-GWU/afwf-project>`_ framework 0.3.1.
- allow field boost for search result sorting by weight.
- allow sortable field for custom result sorting.
- allow custom icon.
- allow download ``.json`` or ``.json.zip`` data file from internet.
- add ``?`` to search query to get help message.

**Minor Improvements**

- reword the user document.


0.0.3 (2021-07-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- Support the End of life Python2.7


0.0.2 (2020-05-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Allow column specified index search settings


0.0.1 (2019-01-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release!
- support ngram, phrase, keyword search.
- easy to custom workflow item.
