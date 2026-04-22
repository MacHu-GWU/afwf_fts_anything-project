.. _Build-Your-Own-Dataset:

Build Your Own Dataset
==============================================================================


Overview
------------------------------------------------------------------------------
This guide walks you through building a custom dataset end-to-end. We will
use a **bookmark manager** as the example — a collection of saved URLs with
titles, tags, and descriptions. The same steps apply to any dataset.

By the end you will have a working Alfred workflow that full-text searches
your bookmarks and opens the selected URL in the browser.


Step 1 — Design Your Data Schema
------------------------------------------------------------------------------
Before writing any files, decide what fields your records will have and how
each one should behave in search.

Ask yourself:

- Which fields do users search against? → these need an indexed type
  (``ngram``, ``text``, ``keyword``)
- Which fields are used only in the display or as the action argument? →
  use ``stored``
- Is there a numeric field to sort by (date, score, priority)? →
  use ``numeric`` with ``indexed`` and ``fast``
- What should pressing ``Enter`` do — open a URL or open a file? →
  that field goes in ``arg_field``

For our bookmarks example:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Reason
   * - ``title``
     - ``ngram``
     - Partial-word search; users type incomplete titles
   * - ``url``
     - ``stored``
     - Used as ``arg_field`` to open in browser; not searched
   * - ``tags``
     - ``text``
     - Full-word search; tags are complete words
   * - ``description``
     - ``text``
     - Full-word phrase search on prose
   * - ``added_at``
     - ``numeric`` (``i64``)
     - Unix timestamp, sortable newest-first


Step 2 — Create the Dataset Directory
------------------------------------------------------------------------------
Choose a short, lowercase name with no spaces (hyphens are fine).
We will use ``bookmarks``.

.. code-block:: bash

    mkdir -p ~/.alfred-afwf/afwf_fts_anything/bookmarks/icons


Step 3 — Write the Data File
------------------------------------------------------------------------------
Create ``~/.alfred-afwf/afwf_fts_anything/bookmarks/bookmarks-data.json``
as a JSON array. Each object must have the same keys you plan to declare in
the setting file:

.. code-block:: javascript

    [
        {
            "title": "Hacker News",
            "url": "https://news.ycombinator.com",
            "tags": "tech news programming",
            "description": "Social news website focusing on computer science and entrepreneurship.",
            "added_at": 1700000000
        },
        {
            "title": "Real Python",
            "url": "https://realpython.com",
            "tags": "python tutorial learning",
            "description": "Python tutorials for developers of all skill levels.",
            "added_at": 1710000000
        },
        {
            "title": "Excalidraw",
            "url": "https://excalidraw.com",
            "tags": "design diagram tool",
            "description": "Virtual whiteboard for sketching hand-drawn like diagrams.",
            "added_at": 1720000000
        }
    ]

**Tips:**

- Every record should have the same keys. Missing keys are treated as empty.
- Values must match the declared field type: a ``numeric`` field must contain
  a number, not a string.
- The file can contain thousands of records — the index is built once and
  queries remain fast regardless of dataset size.


Step 4 — Write the Setting File
------------------------------------------------------------------------------
Create ``~/.alfred-afwf/afwf_fts_anything/bookmarks/bookmarks-setting.json``:

.. code-block:: javascript

    {
        "fields": [
            // partial-word title search, weighted highest
            {"type": "ngram",   "name": "title",       "min_gram": 2, "max_gram": 10, "boost": 2.0},
            // stored only — used as action arg and in title template
            {"type": "stored",  "name": "url"},
            // full-word search on tags and description
            {"type": "text",    "name": "tags",         "boost": 1.5},
            {"type": "text",    "name": "description"},
            // unix timestamp, sortable newest-first
            {"type": "numeric", "name": "added_at",     "kind": "i64", "indexed": true, "fast": true}
        ],
        "sort": [
            {"name": "added_at", "descending": true}
        ],
        "title_field":        "{title}",
        "subtitle_field":     "{tags} | {description}",
        "arg_field":          "{url}",
        "autocomplete_field": "{title}",
        "icon_field":         "bookmark.png"
    }

Refer to :ref:`Setting-and-Data-File` for the full field type reference.


Step 5 — Add an Icon (Optional)
------------------------------------------------------------------------------
Place a PNG icon at:

.. code-block:: bash

    ~/.alfred-afwf/afwf_fts_anything/bookmarks/icons/bookmark.png

If the file does not exist, Alfred uses the workflow's default icon.
Any 256×256 or 512×512 PNG works well.


Step 6 — Create the Alfred Script Filter
------------------------------------------------------------------------------
In Alfred Preferences → Workflows, add a **Script Filter** with:

- **Language**: ``/bin/bash``
- **Argument**: ``Optional``
- **Keyword**: ``bm`` (or any trigger you prefer)
- **Script**:

  .. code-block:: bash

      ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
          --dataset-name 'bookmarks' \
          --query '{query}' \
          --action open_url

Wire the Script Filter to an **Open URL** action. See
:ref:`Alfred-Workflow-Setup` for detailed wiring instructions.


Step 7 — Build the Index and Test
------------------------------------------------------------------------------
Open Alfred and type your keyword:

.. code-block:: text

    bm python

The first query builds the index (takes one to two seconds). You should see
**Real Python** appear. Subsequent queries are instant.

Try:

.. code-block:: text

    bm design     → matches Excalidraw via tags
    bm news       → matches Hacker News
    bm            → all bookmarks, newest first
    bm ?          → reveals bookmarks-setting.json in Finder


Step 8 — Iterate
------------------------------------------------------------------------------
Datasets rarely come out perfect on the first try. A typical iteration cycle:

1. **Edit** ``bookmarks-data.json`` (add records, fix values).
2. **Rebuild** the index:

   .. code-block:: bash

       ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything rebuild-index \
           --dataset-name 'bookmarks'

3. **Test** in Alfred.
4. If results are not what you expect, **tune the setting file**: adjust
   ``boost`` values, switch a field from ``text`` to ``ngram``, or change
   the sort order. Then rebuild again.

.. tip::

    Type ``bm ?`` in Alfred to jump straight to ``bookmarks-setting.json``
    in Finder. Edit, save, rebuild, and test — all without leaving your
    current context.


Hosting Data Remotely
------------------------------------------------------------------------------
If you want to share your dataset with others, or keep it up to date without
manually replacing the local file, host the JSON somewhere and add
``data_url`` to the setting file:

.. code-block:: javascript

    "data_url": "https://example.com/my-bookmarks-data.json"

Supported formats: ``.json`` and ``.json.zip``. The file is downloaded
automatically when the index does not exist or after ``rebuild-index``.
Others who install your workflow only need the ``-setting.json`` file; the
data is fetched for them.
