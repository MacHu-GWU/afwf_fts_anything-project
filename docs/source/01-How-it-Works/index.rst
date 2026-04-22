.. _How-it-Works:

How it Works
==============================================================================


Core Concepts
------------------------------------------------------------------------------
**Setting file**

A JSON file that defines how your data should be indexed and how results should
be rendered in the Alfred dropdown menu. You must create this file manually. It
controls field types, sort order, display templates, and an optional remote data
URL. Comments (``//``) are supported and will be stripped automatically.

**Data file**

A JSON file containing your searchable records — a JSON array of objects, for
example::

    [
        {"key1": "value1", "key2": "value2"},
        {"key1": "value1", "key2": "value2"}
    ]

You can place this file manually, or set ``data_url`` in the setting file to
let the workflow download it automatically on the first run (or after a
``rebuild-index``). ZIP-compressed JSON (``.json.zip``) is also supported.

**Index directory**

The full-text search index, built automatically on the first query from the
data file and setting file. It is powered by `sayt2 <https://github.com/MacHu-GWU/sayt2-project>`_
(backed by `Tantivy <https://github.com/quickwit-oss/tantivy>`_, a Rust-based
search engine). To refresh stale results after updating your data file, use the
``rebuild-index`` command — see :ref`How-it-Works`.

**Icon directory**

An optional ``icons/`` subdirectory inside the dataset folder where you can
place icon images referenced by ``icon_field`` in the setting file. If no icon
is configured, the workflow's default icon is used.

**Project home directory**

All dataset folders live under a single root on your machine:
``~/.alfred-afwf/afwf_fts_anything/``.

**Dataset**

Each dataset is a named folder inside the project home. Given a dataset named
``movie``, the layout is:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/
    └── movie/
        ├── movie-setting.json   ← search configuration (you create this)
        ├── movie-data.json      ← your records (you create this, or set data_url)
        ├── movie-index/         ← search index (auto-generated)
        └── icons/
            └── movie-icon.png   ← optional custom icon


Setting File
------------------------------------------------------------------------------
The setting file has two main responsibilities: defining the search schema and
defining how each result is rendered in Alfred.

**Defining how to search**

Fields are declared as a JSON array under the ``"fields"`` key. Each field
object has a ``"type"`` property that determines how the value is indexed. All
field values are stored by default so they can be used in display templates.

Available field types:

.. list-table::
   :header-rows: 1
   :widths: 15 45 40

   * - Type
     - Purpose
     - Key options
   * - ``stored``
     - Stores the value for display only; not searchable.
     - —
   * - ``ngram``
     - N-gram indexed text. Matches any substring of length between
       ``min_gram`` and ``max_gram``. Ideal for partial-word matching
       (typing ``"god"`` matches ``"godfather"``).
     - ``min_gram`` (default 2), ``max_gram`` (default 10), ``boost``
   * - ``text``
     - Full-word phrase search. The complete word must be spelled correctly.
       Ideal for description or prose fields.
     - ``boost``
   * - ``keyword``
     - Exact-match keyword search. The query must match the stored value.
       Useful for tags or category fields.
     - ``boost``
   * - ``numeric``
     - Numeric field (``i64``, ``f64``, ``u64``). Supports range queries and
       sorting. Requires ``"indexed": true`` and ``"fast": true`` to be sortable.
     - ``kind``, ``indexed``, ``fast``
   * - ``datetime``
     - Datetime field. Supports range queries and sorting.
     - ``indexed``, ``fast``
   * - ``boolean``
     - Boolean field.
     - ``indexed``

To control default result ordering, add a ``"sort"`` array listing field names
and direction:

.. code-block:: javascript

    "sort": [{"name": "rating", "descending": true}]

Only fields with ``"indexed": true`` and ``"fast": true`` (for ``numeric`` /
``datetime``) are sortable.

**Defining how to render results**

In the Alfred dropdown, each result item has five attributes:

- **title** — main line, larger font.
- **subtitle** — second line, smaller font.
- **arg** — value passed to the next workflow action on ``Enter``; also
  copied to clipboard with ``CMD+C``.
- **autocomplete** — text inserted when pressing ``Tab``.
- **icon** — icon image filename, resolved relative to the dataset's
  ``icons/`` directory.

.. image:: ./images/alfred-item.png

Each attribute is configured as a Python ``str.format_map`` template where
``{field_name}`` is replaced by the corresponding value from the matching
document. For example, ``"{title} ({genres}) rate {rating}"`` renders as
``"The Godfather (Crime, Drama) rate 9.2"``.


Movie Dataset Example
------------------------------------------------------------------------------
The following example uses a small IMDB Top 250 dataset.

Data file (``~/.alfred-afwf/afwf_fts_anything/movie/movie-data.json``):

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

Setting file (``~/.alfred-afwf/afwf_fts_anything/movie/movie-setting.json``):

.. code-block:: javascript

    {
        "fields": [
            // store movie_id for display only — not searchable
            {"type": "stored",  "name": "movie_id"},
            // n-gram index on title with boost — partial word matching
            {"type": "ngram",   "name": "title",       "min_gram": 2, "max_gram": 10, "boost": 2.0},
            // full-word phrase search on description
            {"type": "text",    "name": "description"},
            // keyword search on genres with boost
            {"type": "text",    "name": "genres",       "boost": 1.5},
            // numeric field for sorting by rating descending
            {"type": "numeric", "name": "rating",       "kind": "f64", "indexed": true, "fast": true},
            // store url for use as the Alfred arg (action on Enter)
            {"type": "stored",  "name": "url"}
        ],
        "sort": [
            {"name": "rating", "descending": true}
        ],
        "data_url": "https://github.com/MacHu-GWU/afwf_fts_anything-project/releases/download/2.0.1/movie-data.json.zip",
        "title_field":        "{title} ({genres}) rate {rating}",
        "subtitle_field":     "{description}",
        "arg_field":          "{url}",
        "autocomplete_field": "{title}",
        "icon_field":         "movie-icon.png"
    }

What this configuration does:

- ``movie_id`` is stored only, making it available for display templates
  (e.g. copy with ``CMD+C``) but excluded from search.
- ``title`` uses n-gram indexing (2–10 characters). ``"The Shawshank Redemption"``
  is indexed as ``"th"``, ``"he"``, ``"sh"``, ``"ha"``, ``"aw"``, … so
  typing ``"aw"`` already matches it. This is the most user-friendly option
  but uses more disk space.
- ``description`` uses full-word phrase search. Words like ``"imprisoned"``,
  ``"solace"``, ``"redemption"`` are each indexed as a whole. Searching
  ``"two men"`` matches the document because both words appear.
- ``genres`` uses full-word text search with a score boost of 1.5×. Searching
  ``"drama"`` returns all drama movies.
- ``rating`` is a numeric field with ``indexed`` and ``fast`` enabled, making
  it usable as a sort key. The ``sort`` array puts highest-rated movies first.
- The ``data_url`` points to a hosted ZIP of the data file. On ``rebuild-index``
  the workflow re-downloads it automatically.

.. image:: ./images/alfred-item.png


Alfred Workflow Configuration
------------------------------------------------------------------------------
Below is a sample workflow diagram. The Script Filter on the left triggers the
search; the right side connects to "Open URL", "Open File", and
"Reveal in Finder" actions. Selecting an item and pressing ``Enter`` passes the
``arg`` (the IMDB URL) to "Open URL", opening the page in your default browser.

.. image:: ./images/alfred-workflow-diagram.png

The Script Filter script uses ``uvx`` — no installation, no virtualenv, no
Python path configuration required:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
        --dataset-name 'movie' \
        --query '{query}'

Below is a sample Script Filter configuration panel. Key points:

- The **Keyword** (e.g. ``fts movie``) is what you type in Alfred to trigger
  this workflow.
- **Argument Optional** means the workflow accepts both an empty input and a
  typed query.
- **Language** must be ``/bin/bash``.
- The **Script** field contains the ``uvx`` command above. To search a
  different dataset, change ``--dataset-name 'movie'`` to your dataset name.

.. image:: ./images/alfred-workflow-configuration.png


Special Queries
------------------------------------------------------------------------------
- **Empty query** — returns all documents in the dataset, sorted by the
  configured ``sort`` fields.
- ``?`` — instead of searching, reveals the dataset's setting file in Finder.
  Useful for quick edits without leaving Alfred.


Next
------------------------------------------------------------------------------
See :ref`How-it-Works` for step-by-step setup
instructions.
