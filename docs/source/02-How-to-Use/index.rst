.. _How-to-Use:

How to Use
==============================================================================


Prerequisites
------------------------------------------------------------------------------
- `Alfred 5+ <https://www.alfredapp.com/>`_ installed on macOS.
- `Powerpack <https://www.alfredapp.com/powerpack/>`_ purchased — required to
  use Alfred Workflows.
- `uv <https://github.com/astral-sh/uv>`_ installed. ``uv`` provides the
  ``uvx`` tool that runs ``afwf-fts-anything`` without any manual installation.
  If you do not have it yet:

  .. code-block:: bash

      curl -LsSf https://astral.sh/uv/install.sh | sh

  This places ``uvx`` at ``~/.local/bin/uvx``.

That's all. You do **not** need to install ``afwf-fts-anything`` manually, set
up a virtual environment, or configure a Python path. ``uvx`` downloads and
caches the package automatically on first use.


Quick Start with the Sample Movie Dataset
------------------------------------------------------------------------------
The movie dataset is a great way to verify everything is working before you
bring your own data.

**Step 1 — Create the dataset directory:**

.. code-block:: bash

    mkdir -p ~/.alfred-afwf/afwf_fts_anything/movie/icons

**Step 2 — Download the sample files** from the
`GitHub Releases page <https://github.com/MacHu-GWU/afwf_fts_anything-project/releases>`_
and place them as follows:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/
    └── movie/
        ├── movie-setting.json
        ├── movie-data.json          ← or omit this and rely on data_url
        └── icons/
            └── movie-icon.png

Alternatively, if ``data_url`` is set in ``movie-setting.json``, you can skip
placing ``movie-data.json`` — the workflow downloads it automatically the first
time you trigger a search or run ``rebuild-index``.

**Step 3 — Create the Alfred workflow:**

In Alfred Preferences → Workflows, create a new blank workflow. Add a
**Script Filter** object with these settings:

- **Language**: ``/bin/bash``
- **Script**:

  .. code-block:: bash

      ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
          --dataset-name 'movie' \
          --query '{query}'

- **Keyword**: ``fts movie`` (or any trigger phrase you prefer)
- **Argument**: Optional

Connect the Script Filter to an **Open URL** action (Alfred will pass the IMDB
URL from ``arg_field`` directly to it).

**Step 4 — Test it:**

Type ``fts movie godfather`` in Alfred. On the very first query the index is
built from the data file, which takes a moment. Every subsequent query is
near-instant.

Try also:

- ``fts movie drama`` — matches all drama movies
- ``fts movie`` (empty) — lists all 9 movies sorted by rating descending
- ``fts movie ?`` — reveals the ``movie-setting.json`` file in Finder


Bring Your Own Dataset
------------------------------------------------------------------------------
Make sure you have read `How it Works <../01-How-it-Works/index.html>`_ first.

1. **Choose a name** for your dataset, e.g. ``mydata``.

2. **Create the dataset directory:**

   .. code-block:: bash

       mkdir -p ~/.alfred-afwf/afwf_fts_anything/mydata/icons

3. **Write your data file** at
   ``~/.alfred-afwf/afwf_fts_anything/mydata/mydata-data.json``.
   It must be a JSON array of objects where each object represents one
   searchable record.

4. **Write your setting file** at
   ``~/.alfred-afwf/afwf_fts_anything/mydata/mydata-setting.json``.
   Use the movie example as a template and adjust field names, types, and
   display templates to match your data schema.

5. **Create a new Alfred Script Filter** (or duplicate an existing one) with
   the script:

   .. code-block:: bash

       ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
           --dataset-name 'mydata' \
           --query '{query}'

6. **Type your keyword** in Alfred to trigger a search. The index is built
   automatically on the first query.


Rebuilding the Index
------------------------------------------------------------------------------
The index is built once and reused on every subsequent query. If you update
``mydata-data.json`` (or want to pull fresh data from ``data_url``), you need
to rebuild:

**Option A — from Alfred:**

Create a second workflow with a Script Filter connected to a Run Script action:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything rebuild-index \
        --dataset-name 'mydata'

**Option B — from the built-in reset workflow:**

Add a Script Filter that lists all datasets available for reset:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything list-datasets-for-reset \
        --dataset-name-query '{query}'

Selecting a dataset from the list automatically triggers ``rebuild-index`` for
it. This is useful if you manage many datasets.

**Option C — from Terminal:**

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything rebuild-index \
        --dataset-name 'mydata'


Upgrading to a New Version
------------------------------------------------------------------------------
To pin a newer release, update the version number in the ``uvx`` command:

.. code-block:: bash

    # change 2.0.1 to the new version in every Script Filter script
    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.2" afwf-fts-anything fts \
        --dataset-name 'movie' \
        --query '{query}'

``uvx`` will download the new version automatically on first use and cache it
locally. No other action is required.


FAQ
------------------------------------------------------------------------------
**Q: Why JSON instead of CSV?**

JSON supports nested structures, multi-line text, and mixed types natively —
all things that CSV handles poorly or inconsistently across applications.

**Q: My search still returns old results after I updated my data file.**

Run ``rebuild-index`` for that dataset (see above). The old index is deleted
and rebuilt from the current data file.

**Q: The first query is slow.**

The index is being built from scratch. This happens once per dataset (and again
after each ``rebuild-index``). All subsequent queries are near-instant because
they hit the pre-built Tantivy index on disk.

**Q: Can I host my data file remotely?**

Yes. Add a ``"data_url"`` key to your setting file pointing to a ``.json`` or
``.json.zip`` URL. The workflow downloads and caches it on the first run or
after ``rebuild-index``. This is useful for sharing datasets — users only need
the setting file; the data is fetched automatically.

**Q: Can I use this without Alfred (e.g. from the command line)?**

Yes. The CLI works standalone:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything fts \
        --dataset-name 'movie' \
        --query 'godfather'

The output is Alfred's Script Filter JSON, which you can pipe or inspect
directly.
