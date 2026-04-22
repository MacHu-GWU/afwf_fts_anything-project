.. _Setting-and-Data-File:

Setting File & Data File
==============================================================================


Overview
------------------------------------------------------------------------------
A dataset is made of two files you write and one directory that is generated
automatically:

.. code-block:: text

    movie/
    ├── movie-setting.json   ← defines the schema and display rules
    ├── movie-data.json      ← the records to search
    └── movie-index/         ← built automatically from the two files above

The **setting file** is the schema: it tells the engine which fields exist,
how each one is indexed, how results should be sorted, and how each hit should
look inside Alfred. The **data file** is the content: a plain JSON array where
every object's keys must match the field names declared in the setting.


Data File
------------------------------------------------------------------------------
The data file is a JSON array of objects. Each object is one searchable
record. The keys are free-form — you define them, and they must match the
field names in the setting file.

.. code-block:: javascript

    [
        {
            "movie_id": 1,
            "title": "The Shawshank Redemption",
            "description": "Two imprisoned men bond over a number of years...",
            "genres": "Drama",
            "rating": 9.2,
            "url": "https://www.imdb.com/title/tt0111161"
        },
        {
            "movie_id": 2,
            "title": "The Godfather",
            ...
        }
    ]

There are no required keys. Use whatever fields make sense for your data.

**Providing data:**

- **Local file** — place ``{name}-data.json`` in the dataset folder manually.
- **Remote file** — set ``data_url`` in the setting file (see below). The
  workflow downloads and saves the file automatically on the first query or
  after a ``rebuild-index``. Both ``.json`` and ``.json.zip`` URLs are
  supported.


Setting File
------------------------------------------------------------------------------
The setting file is a JSON file (with ``//`` comment support) that has four
responsibilities: field definitions, sort order, display templates, and
optional remote data download.

.. code-block:: javascript

    {
        "fields": [ ... ],          // required — field schema
        "sort":   [ ... ],          // optional — default sort order
        "data_url": "https://...",  // optional — remote data source

        "title_field":        "...", // required — Alfred result title
        "subtitle_field":     "...", // optional — Alfred result subtitle
        "arg_field":          "...", // optional — value passed on Enter
        "autocomplete_field": "...", // optional — Tab completion text
        "icon_field":         "..."  // optional — icon filename
    }


Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``fields`` array declares every column in your dataset. Each entry is a
JSON object with a ``"type"`` key that controls how the value is indexed.

**Stored field** — value is saved for display only; not searchable.

.. code-block:: javascript

    {"type": "stored", "name": "movie_id"}
    {"type": "stored", "name": "url"}

Use ``stored`` for any field you need in display templates or as an action
argument, but do not need to search against.

----

**N-gram field** — indexes every substring of length ``min_gram`` to
``max_gram``. Partial-word typing works: ``"god"`` matches ``"godfather"``.
Best for title-like fields where users type incomplete words.

.. code-block:: javascript

    {
        "type": "ngram",
        "name": "title",
        "min_gram": 2,
        "max_gram": 10,
        "boost": 2.0
    }

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Option
     - Default
     - Description
   * - ``min_gram``
     - ``2``
     - Minimum n-gram length. Shorter = more matches, larger index.
   * - ``max_gram``
     - ``10``
     - Maximum n-gram length.
   * - ``boost``
     - ``1.0``
     - Score multiplier. Hits on this field count more toward ranking.

----

**Text field** — standard full-word phrase search. The full word must be
spelled correctly. ``"imprisoned"`` matches ``"imprisoned"``; ``"impriso"``
does not.

.. code-block:: javascript

    {"type": "text", "name": "description"}
    {"type": "text", "name": "genres", "boost": 1.5}

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Option
     - Default
     - Description
   * - ``boost``
     - ``1.0``
     - Score multiplier.

----

**Keyword field** — exact-match search against whole tokens. The query
must match a stored keyword exactly (case-insensitive). Useful for category
or tag fields.

.. code-block:: javascript

    {"type": "keyword", "name": "status"}

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Option
     - Default
     - Description
   * - ``boost``
     - ``1.0``
     - Score multiplier.

----

**Numeric field** — stores and optionally indexes a number. Set both
``"indexed": true`` and ``"fast": true`` to make the field sortable.

.. code-block:: javascript

    {
        "type": "numeric",
        "name": "rating",
        "kind": "f64",
        "indexed": true,
        "fast": true
    }

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Option
     - Default
     - Description
   * - ``kind``
     - ``"f64"``
     - Numeric type: ``"i64"`` (signed integer), ``"u64"`` (unsigned integer),
       or ``"f64"`` (floating point).
   * - ``indexed``
     - ``false``
     - If ``true``, the field can be used in range queries and sorting.
   * - ``fast``
     - ``false``
     - If ``true`` (requires ``indexed``), the field can be used as a sort key.

----

**Datetime field** — same as numeric but for timestamps.

.. code-block:: javascript

    {"type": "datetime", "name": "created_at", "indexed": true, "fast": true}

----

**Boolean field** — stores a boolean value.

.. code-block:: javascript

    {"type": "boolean", "name": "is_active", "indexed": true}


Sort
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The optional ``sort`` array specifies the default ordering when multiple
documents match a query. List fields in priority order:

.. code-block:: javascript

    "sort": [
        {"name": "rating", "descending": true}
    ]

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Option
     - Default
     - Description
   * - ``name``
     - —
     - Field name. Must be a ``numeric`` or ``datetime`` field with
       ``"indexed": true`` and ``"fast": true``.
   * - ``descending``
     - ``false``
     - ``true`` for highest-first (rating, date), ``false`` for lowest-first.


Remote Data (data_url)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If your dataset is hosted remotely, set ``data_url`` to a direct download
link. Supported formats: ``.json`` and ``.json.zip`` (the first ``.json``
file inside the ZIP is used).

.. code-block:: javascript

    "data_url": "https://github.com/owner/repo/releases/download/v1.0/data.json.zip"

The file is downloaded and saved as ``{name}-data.json`` in the dataset
folder. It is only fetched when the index does not exist yet, or when you
explicitly run ``rebuild-index``.


Display Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The five template keys control what Alfred shows for each result. Each value
is a Python ``str.format_map`` template: ``{field_name}`` is replaced by the
corresponding value from the matched document.

All fields referenced in a template must exist and be stored (i.e. declared
as ``stored``, or any other type — all types store their value by default).

.. code-block:: javascript

    "title_field":        "{title} ({genres}) rate {rating}",
    "subtitle_field":     "{description}",
    "arg_field":          "{url}",
    "autocomplete_field": "{title}",
    "icon_field":         "movie-icon.png"

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Key
     - Description
   * - ``title_field``
     - **Required.** Main line in the Alfred dropdown (larger text). If
       omitted, a field named ``"title"`` must exist in ``fields``.
   * - ``subtitle_field``
     - Second line in the Alfred dropdown (smaller text).
   * - ``arg_field``
     - Value passed to the next Alfred action when the user presses ``Enter``
       (e.g. a URL for Open URL, a file path for Open File). Also copied to
       clipboard with ``CMD+C``.
   * - ``autocomplete_field``
     - Text inserted into the Alfred input when the user presses ``Tab``.
   * - ``icon_field``
     - Icon filename. Resolved relative to the ``icons/`` subdirectory inside
       the dataset folder (see below).


Icons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Icon files live in the ``icons/`` subdirectory of the dataset folder:

.. code-block:: text

    movie/
    └── icons/
        ├── movie-icon.png      ← one icon for all results
        ├── drama.png           ← or per-result icons
        └── action.png

``icon_field`` is a template like any other display field. It can be a fixed
filename:

.. code-block:: javascript

    "icon_field": "movie-icon.png"

Or it can be dynamic, built from a field value in the record:

.. code-block:: javascript

    "icon_field": "{genre_icon}"   // each record has a "genre_icon" field like "drama.png"

The resolved path is always ``{dataset_folder}/icons/{icon_field_value}``. If
the file does not exist, Alfred falls back to the workflow's default icon.


JSON Comment Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Setting files support ``//`` single-line comments anywhere in the JSON. They
are stripped before parsing, so you can annotate your configuration freely:

.. code-block:: javascript

    {
        "fields": [
            // store only — not searchable
            {"type": "stored", "name": "movie_id"},
            // n-gram for partial-word title search
            {"type": "ngram",  "name": "title", "min_gram": 2, "max_gram": 10}
        ],
        "title_field": "{title} ({genres}) rate {rating}" // shown in Alfred
    }


Complete Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The full movie setting file with all options annotated:

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
