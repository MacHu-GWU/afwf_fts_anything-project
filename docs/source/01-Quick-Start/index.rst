.. _Quick-Start:

Quick Start
==============================================================================
This guide gets you from zero to a working search workflow in about five
minutes. You will install the sample **movie dataset**, import the pre-built
Alfred workflow, and run your first search query.


Prerequisites
------------------------------------------------------------------------------
- **macOS** with `Alfred 5+ <https://www.alfredapp.com/>`_ installed.
- `Alfred Powerpack <https://www.alfredapp.com/powerpack/>`_ activated
  (required to use Alfred Workflows).


Step 1 — Install uv
------------------------------------------------------------------------------
``afwf_fts_anything`` runs via `uvx <https://docs.astral.sh/uv/guides/tools/>`_,
which is part of the `uv <https://github.com/astral-sh/uv>`_ toolchain. You
do **not** need to install ``afwf_fts_anything`` manually — ``uvx`` downloads
and caches it automatically on first use.

If you do not have ``uv`` yet, open a Terminal and run:

.. code-block:: bash

    curl -LsSf https://astral.sh/uv/install.sh | sh

Verify the installation:

.. code-block:: bash

    ~/.local/bin/uvx --version

You should see a version string. That is all you need.


Step 2 — Download and Import the Alfred Workflow
------------------------------------------------------------------------------
1. Go to the `GitHub Releases page <https://github.com/MacHu-GWU/afwf_fts_anything-project/releases>`_.
2. Find the latest release (2.0.1 or newer).
3. Download the file named ``afwf_fts_anything-x.x.x.alfredworkflow``.
4. **Double-click** the downloaded file. Alfred opens and asks you to
   confirm the import. Click **Import**.

The workflow is now installed in Alfred. It contains a ready-to-use
Script Filter for the sample movie dataset.


Step 3 — Set Up the Sample Movie Dataset
------------------------------------------------------------------------------
The sample dataset (IMDB Top 250 movies) is hosted on GitHub. Run the
following command in Terminal to download it and place it in the correct
location automatically:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything setup-sample-data

This command:

- Creates the directory ``~/.alfred-afwf/afwf_fts_anything/movie/``
- Downloads ``movie-data.json`` and ``movie-setting.json`` into that directory
- Downloads the ``movie-icon.png`` icon into ``icons/``

You should see output confirming each file was placed successfully.


Step 4 — Run Your First Search
------------------------------------------------------------------------------
Open Alfred (default shortcut: ``⌥Space``) and type:

.. code-block:: text

    fts-movie godfather

You should see **The Godfather** appear in the dropdown with its rating and
description. On the very first query the search index is built from the data
file, which takes a second or two. Every subsequent query is near-instant.

Try a few more:

.. code-block:: text

    fts-movie drama        → all drama movies, sorted by rating
    fts-movie redemption   → matches "Shawshank" via n-gram on description
    fts-movie             → (empty query) shows all 9 movies
    fts-movie ?           → reveals movie-setting.json in Finder

Press ``Enter`` on any result to open its IMDB page in your browser.
Press ``CMD+C`` to copy the URL to the clipboard instead.


Troubleshooting
------------------------------------------------------------------------------
**"No results found" on every query**

The data file or setting file may not be in the right place. Check that these
files exist:

.. code-block:: bash

    ls ~/.alfred-afwf/afwf_fts_anything/movie/

You should see ``movie-data.json``, ``movie-setting.json``, and an ``icons/``
directory. If any are missing, re-run the setup command from Step 3.

----

**First query is very slow or times out**

The index is being built for the first time. Alfred Script Filters have a
timeout; if the build exceeds it, Alfred may show no results on that first
attempt. Simply search again — the index will already be built and the
response will be instant.

----

**Alfred shows "Permission denied" or "command not found"**

Make sure ``uvx`` is at ``~/.local/bin/uvx``. Run:

.. code-block:: bash

    ls -la ~/.local/bin/uvx

If the file is missing, re-run the ``uv`` install command from Step 1. If it
exists but Alfred can not find it, verify that the Script Filter in the
workflow uses the full path ``~/.local/bin/uvx`` (not just ``uvx``). Alfred
does not inherit your shell's ``$PATH``.

----

**Results are stale after I edited** ``movie-data.json``

The index is cached on disk and is not rebuilt automatically. Open Alfred and
use the built-in reset workflow (if included in the ``.alfredworkflow``), or
run from Terminal:

.. code-block:: bash

    ~/.local/bin/uvx --from "afwf-fts-anything==2.0.1" afwf-fts-anything rebuild-index \
        --dataset-name 'movie'

----

**I want to search my own data, not the movie sample**

See `Build Your Own Dataset <../05-Build-Your-Own-Dataset/index.html>`_ for a
step-by-step walkthrough.
