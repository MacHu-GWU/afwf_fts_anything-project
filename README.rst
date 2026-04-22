
.. image:: https://readthedocs.org/projects/afwf-fts-anything/badge/?version=latest
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/afwf_fts_anything-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/pypi/v/afwf-fts-anything.svg
    :target: https://pypi.python.org/pypi/afwf-fts-anything

.. image:: https://img.shields.io/pypi/l/afwf-fts-anything.svg
    :target: https://pypi.python.org/pypi/afwf-fts-anything

.. image:: https://img.shields.io/pypi/pyversions/afwf-fts-anything.svg
    :target: https://pypi.python.org/pypi/afwf-fts-anything

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/afwf-fts-anything#files


Full-Text Search Anything — Alfred Workflow + Python Library
==============================================================================
.. image:: https://afwf-fts-anything.readthedocs.io/en/latest/_static/afwf_fts_anything-logo.png
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/

.. image:: https://user-images.githubusercontent.com/6800411/50622795-1fc45580-0ede-11e9-878c-64e2ab6292b1.gif


You Decide What Happens
------------------------------------------------------------------------------
Every search result is an action waiting to trigger. When you press ``Enter``
on a result, ``afwf_fts_anything`` can:

- **Open a URL** — jump straight to a web page (IMDB movie page, AWS docs,
  GitHub issue, anything with a link).
- **Open a file** — open a local file in its default application, or reveal
  it in Finder.

You configure the action once in the Alfred Script Filter:

.. code-block:: bash

    # open a URL on Enter
    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
        --dataset-name 'movie' --query '{query}' --action open_url

    # open a local file on Enter
    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
        --dataset-name 'movie' --query '{query}' --action open_file

No installation, no virtual environment. ``uvx`` handles everything.


Your Data, Your Schema
------------------------------------------------------------------------------
The dataset is a plain JSON file — a list of objects, any fields you want:

.. code-block:: javascript

    [
        {
            "movie_id": 1,
            "title": "The Shawshank Redemption",
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "genres": "Drama",
            "rating": 9.2,
            "url": "https://www.imdb.com/title/tt0111161"
        },
        {
            "movie_id": 2,
            "title": "The Godfather",
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "genres": "Crime, Drama",
            "rating": 9.2,
            "url": "https://www.imdb.com/title/tt0068646"
        },
        ...
    ]

It could be movies, bookmarks, API references, Terraform resources, local
files — anything you can put in a JSON array.


Your Config, Your Search Behavior
------------------------------------------------------------------------------
A single JSON setting file controls how fields are indexed, how results are
sorted, and what Alfred displays:

.. code-block:: javascript

    {
        "fields": [
            // store only — not searchable, but available in display templates
            {"type": "stored",  "name": "movie_id"},
            // n-gram: typing "god" already matches "godfather"
            {"type": "ngram",   "name": "title",       "min_gram": 2, "max_gram": 10, "boost": 2.0},
            // full-word phrase search on description
            {"type": "text",    "name": "description"},
            // full-word text search on genres with a relevance boost
            {"type": "text",    "name": "genres",       "boost": 1.5},
            // numeric field, sortable by rating descending
            {"type": "numeric", "name": "rating",       "kind": "f64", "indexed": true, "fast": true},
            // stored for use as the action argument (URL or file path)
            {"type": "stored",  "name": "url"}
        ],
        // default sort order: highest rated first
        "sort": [{"name": "rating", "descending": true}],
        // optional: auto-download data on first run / rebuild
        "data_url": "https://github.com/MacHu-GWU/afwf_fts_anything-project/releases/download/1.1.1/movie-data.json.zip",
        // Alfred display templates — {field_name} is replaced per result
        "title_field":        "{title} ({genres}) rate {rating}",
        "subtitle_field":     "{description}",
        "arg_field":          "{url}",
        "autocomplete_field": "{title}",
        "icon_field":         "movie-icon.png"
    }

Comments (``//``) are supported and stripped automatically.


Alfred Owns the UI
------------------------------------------------------------------------------
There is no custom UI code to write. Everything visible in Alfred — the
dropdown list, keyboard navigation, icons, subtitles, clipboard copy
(``CMD+C``), tab-autocomplete — is standard Alfred behavior. You wire it
together with one ``uvx`` command in a Script Filter:

.. image:: ./docs/source/01-User-Guide/01-How-it-Works/images/alfred-workflow-configuration.png

The only thing you touch is the Script field. Everything else is Alfred.


Also a Python Library
------------------------------------------------------------------------------
``afwf_fts_anything`` is built on `sayt2 <https://github.com/MacHu-GWU/sayt2-project>`_
(powered by `Tantivy <https://github.com/quickwit-oss/tantivy>`_, written in
Rust) and works as a standalone Python full-text search library with no Alfred
dependency. Build an index from any JSON dataset and query it directly:

.. code-block:: python

    from pathlib import Path
    from afwf_fts_anything.api import DataCatalog

    # point to the directory that holds your dataset folders
    catalog = DataCatalog(
        dir_root=Path("~/.alfred-afwf/afwf_fts_anything").expanduser()
    )

    # get a dataset by name — reads movie-setting.json automatically
    dataset = catalog.get_dataset("movie")

    # build the index on first use (skipped if already built)
    dataset.build_index()

    # search and get plain dicts back
    results = dataset.search("godfather", limit=10)
    for doc in results:
        print(doc["title"], doc["rating"])


Documentation
------------------------------------------------------------------------------
Full documentation — Quick Start, Setting File Reference, Alfred Workflow
Setup, and a step-by-step guide to building your own dataset:

📖 `https://afwf-fts-anything.readthedocs.io/en/latest/ <https://afwf-fts-anything.readthedocs.io/en/latest/>`_


Projects Built on ``afwf_fts_anything``
------------------------------------------------------------------------------
- `AWS CloudFormation Resource & Property Reference <https://github.com/MacHu-GWU/alfred-cloudformation-resource-property-ref>`_ — jump to official CloudFormation docs
- `Terraform AWS Resource Reference <https://github.com/MacHu-GWU/alfred-terraform-resource-property-ref>`_ — jump to official Terraform docs
- `AWS Python Boto3 API Reference <https://github.com/MacHu-GWU/alfred-python-boto3-ref>`_ — jump to Boto3 service/method docs
