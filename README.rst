
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

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/afwf-fts-anything#files


The Alfred Workflow: Full Text Search Anything
==============================================================================
.. image:: https://afwf-fts-anything.readthedocs.io/en/latest/_static/afwf_fts_anything-logo.png
    :target: https://afwf-fts-anything.readthedocs.io/en/latest/


Introduction
------------------------------------------------------------------------------
``afwf_fts_anything`` is an `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ that enables full-text search on your own custom datasets, and uses the results to open a URL, open a file, run a script, or do virtually anything. Traditionally, this would require setting up an `Elasticsearch <https://github.com/elastic/elasticsearch>`_ server, learning data ingestion APIs, and building a custom Alfred workflow from scratch. ``afwf_fts_anything`` removes all those obstacles — just provide your dataset and a search configuration file.

**Version 2.0 is a complete rewrite.** The underlying search engine has been upgraded to `sayt2 <https://github.com/MacHu-GWU/sayt2-project>`_ (powered by `Tantivy <https://github.com/quickwit-oss/tantivy>`_), delivering significantly faster indexing and search. The configuration format has been redesigned with explicit, typed field definitions. Most importantly, **no installation or Python environment setup is required** — the workflow runs via ``uvx``, which handles everything automatically.

**Demo**

.. image:: https://user-images.githubusercontent.com/6800411/50622795-1fc45580-0ede-11e9-878c-64e2ab6292b1.gif


What's New in 2.0
------------------------------------------------------------------------------
- **Zero-dependency installation**: The Alfred workflow script runs via ``uvx`` (from `uv <https://github.com/astral-sh/uv>`_). No manual ``pip install``, no virtualenv management. The first run downloads the package automatically; subsequent runs use a local cache.
- **New configuration format**: Fields are now defined as typed objects (``stored``, ``ngram``, ``text``, ``keyword``, ``numeric``, ``datetime``, ``boolean``) replacing the old boolean-flag style.
- **Sort support**: The ``sort`` key in the setting file controls the default result ordering (e.g. sort movies by rating descending).
- **Remote data download**: Add a ``data_url`` pointing to a ``.json`` or ``.json.zip`` file and the workflow will download and cache your dataset automatically.
- **Action support**: Each search result can trigger ``open_url`` (default) or ``open_file``, configured per workflow.
- **Special queries**: Type ``?`` to reveal the dataset's setting file in Finder for quick editing. An empty query returns all documents.


How It Works
------------------------------------------------------------------------------
The workflow reads dataset files from a dedicated project-home directory:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/
    └── {dataset_name}/
        ├── {dataset_name}-setting.json   ← search configuration
        ├── {dataset_name}-data.json      ← your records (JSON array)
        ├── {dataset_name}-index/         ← search index (auto-generated)
        └── icons/
            └── {icon_files}

On the first search query, the index is built from ``{dataset_name}-data.json``. All subsequent queries hit the pre-built index directly for near-instant results. To refresh the index after updating your data, use the ``rebuild-index`` command from the Alfred workflow.


Setup Guide
------------------------------------------------------------------------------

**Step 1 — Install uv**

If you do not already have ``uv`` installed, run:

.. code-block:: bash

    curl -LsSf https://astral.sh/uv/install.sh | sh

This places ``uvx`` at ``~/.local/bin/uvx``.

**Step 2 — Create your dataset directory**

Create a folder for your dataset under the project home:

.. code-block:: bash

    mkdir -p ~/.alfred-afwf/afwf_fts_anything/movie
    mkdir -p ~/.alfred-afwf/afwf_fts_anything/movie/icons

**Step 3 — Add your data and setting files**

Place ``movie-data.json`` and ``movie-setting.json`` (see examples below) into ``~/.alfred-afwf/afwf_fts_anything/movie/``.

**Step 4 — Configure your Alfred Script Filter**

In Alfred Preferences, create a new workflow with a **Script Filter** object. Set the language to ``/bin/bash`` and use this script:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts --dataset-name 'movie' --query '{query}'

That's it. The first run will download the package and build the index; every run after that is instant.


Movie Dataset Example
------------------------------------------------------------------------------

This example uses a small IMDB Top 250 dataset to demonstrate the full workflow.

**Data file** (``movie-data.json``):

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
        {
            "movie_id": 3,
            "title": "The Dark Knight",
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "genres": "Action, Crime, Drama",
            "rating": 9.0,
            "url": "https://www.imdb.com/title/tt0468569"
        },
        {
            "movie_id": 4,
            "title": "12 Angry Men",
            "description": "The jury in a New York City murder trial is frustrated by a single member whose skeptical caution forces them to more carefully consider the evidence before jumping to a hasty verdict.",
            "genres": "Crime, Drama",
            "rating": 9.0,
            "url": "https://www.imdb.com/title/tt0050083"
        },
        {
            "movie_id": 5,
            "title": "Schindler's List",
            "description": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
            "genres": "Biography, Drama, History",
            "rating": 8.9,
            "url": "https://www.imdb.com/title/tt0108052"
        },
        {
            "movie_id": 6,
            "title": "The Lord of the Rings: The Return of the King",
            "description": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.",
            "genres": "Action, Adventure, Drama",
            "rating": 8.9,
            "url": "https://www.imdb.com/title/tt0167260"
        },
        {
            "movie_id": 7,
            "title": "Pulp Fiction",
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "genres": "Crime, Drama",
            "rating": 8.8,
            "url": "https://www.imdb.com/title/tt0110912"
        },
        {
            "movie_id": 8,
            "title": "Fight Club",
            "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
            "genres": "Drama",
            "rating": 8.7,
            "url": "https://www.imdb.com/title/tt0137523"
        },
        {
            "movie_id": 9,
            "title": "Saving Private Ryan",
            "description": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.",
            "genres": "Drama, War",
            "rating": 8.6,
            "url": "https://www.imdb.com/title/tt0120815"
        }
    ]

**Setting file** (``movie-setting.json``):

.. code-block:: javascript

    {
        "fields": [
            {"type": "stored",  "name": "movie_id"},
            {"type": "ngram",   "name": "title",       "min_gram": 2, "max_gram": 10, "boost": 2.0},
            {"type": "text",    "name": "description"},
            {"type": "text",    "name": "genres",       "boost": 1.5},
            {"type": "numeric", "name": "rating",       "kind": "f64", "indexed": true, "fast": true},
            {"type": "stored",  "name": "url"}
        ],
        "sort": [
            {"name": "rating", "descending": true}
        ],
        "data_url": "https://github.com/MacHu-GWU/afwf_fts_anything-project/releases/download/1.1.1/movie-data.json.zip",
        "title_field":        "{title} ({genres}) rate {rating}",
        "subtitle_field":     "{description}",
        "arg_field":          "{url}",
        "autocomplete_field": "{title}",
        "icon_field":         "movie-icon.png"
    }

.. note::

    ``afwf_fts_anything`` supports ``//`` comments in JSON files — you do not need to remove them.


Field Types Reference
------------------------------------------------------------------------------

Each entry in the ``fields`` array is an object with a ``"type"`` key. Available types:

+----------------+--------------------------------------------------------+------------------------------+
| Type           | Purpose                                                | Key options                  |
+================+========================================================+==============================+
| ``stored``     | Stores the value for display; not searchable           | —                            |
+----------------+--------------------------------------------------------+------------------------------+
| ``ngram``      | N-gram indexed text; good for partial-word matching    | ``min_gram``, ``max_gram``,  |
|                | (e.g. typing "god" finds "godfather")                  | ``boost``                    |
+----------------+--------------------------------------------------------+------------------------------+
| ``text``       | Full phrase/word indexed text                          | ``boost``                    |
+----------------+--------------------------------------------------------+------------------------------+
| ``keyword``    | Exact-match keyword field (case-insensitive optional)  | ``boost``                    |
+----------------+--------------------------------------------------------+------------------------------+
| ``numeric``    | Numeric field (``i64``, ``f64``, ``u64``); supports    | ``kind``, ``indexed``,       |
|                | range queries and sorting                              | ``fast``                     |
+----------------+--------------------------------------------------------+------------------------------+
| ``datetime``   | Datetime field; supports range queries and sorting     | ``indexed``, ``fast``        |
+----------------+--------------------------------------------------------+------------------------------+
| ``boolean``    | Boolean field                                          | ``indexed``                  |
+----------------+--------------------------------------------------------+------------------------------+

To make a field **sortable**, set ``"indexed": true`` and ``"fast": true`` (required for ``numeric`` / ``datetime``), then list it in the ``"sort"`` array.

To **display** a field in Alfred results (``title_field``, ``subtitle_field``, etc.), the field must have ``stored=true``. All field types store their value by default except when explicitly disabled.


Template Fields
------------------------------------------------------------------------------

The following keys in the setting file use Python ``str.format_map`` templates where ``{field_name}`` is replaced by the corresponding value from each document:

- ``title_field`` — main line shown in Alfred's dropdown
- ``subtitle_field`` — second line shown in Alfred's dropdown
- ``arg_field`` — value passed to the next workflow action (e.g. a URL or file path)
- ``autocomplete_field`` — text inserted when pressing Tab
- ``icon_field`` — icon filename (resolved relative to the dataset's ``icons/`` directory)


CLI Commands
------------------------------------------------------------------------------

All commands are invoked via ``afwf-fts-anything`` (or via ``uvx`` as shown above).

**Search a dataset**

.. code-block:: bash

    afwf-fts-anything fts --dataset-name 'movie' --query 'godfather'

- ``--dataset-name``: name of the dataset directory under the project home
- ``--query``: search string; empty string returns all documents; ``?`` reveals the setting file in Finder
- ``--action``: ``open_url`` (default) or ``open_file``

**Rebuild the search index**

.. code-block:: bash

    afwf-fts-anything rebuild-index --dataset-name 'movie'

Deletes the existing index, optionally re-downloads the remote data (if ``data_url`` is set), and rebuilds from scratch. Use this after updating ``movie-data.json``.

**List all datasets (for the reset workflow)**

.. code-block:: bash

    afwf-fts-anything list-datasets-for-reset --dataset-name-query ''

Returns all valid datasets under the project home, with optional fuzzy filtering. Each result triggers ``rebuild-index`` when selected in Alfred.


Alfred Workflow Script Examples
------------------------------------------------------------------------------

**Script Filter — search:**

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
        --dataset-name 'movie' \
        --query '{query}'

**Script Filter — list datasets to rebuild:**

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything list-datasets-for-reset \
        --dataset-name-query '{query}'

**Run Script — rebuild a specific index:**

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything rebuild-index \
        --dataset-name 'movie'


Projects based on ``afwf_fts_anything``
------------------------------------------------------------------------------
- Search `AWS CloudFormation Resource and Property Reference <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html>`_, quickly jump to Official AWS CloudFormation Resource and Property Document: https://github.com/MacHu-GWU/alfred-cloudformation-resource-property-ref
- Search `Terraform AWS Resource Reference <https://registry.terraform.io/providers/hashicorp/aws/latest/docs>`_, quickly jump to Official Terraform AWS Resource Document: https://github.com/MacHu-GWU/alfred-terraform-resource-property-ref
- Search `AWS Python Boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html>`_ API Reference: https://github.com/MacHu-GWU/alfred-python-boto3-ref
