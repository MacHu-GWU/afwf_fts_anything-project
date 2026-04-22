.. _Data-Catalog:

Data Catalog
==============================================================================
The **Data Catalog** is the single directory on your machine where
``afwf_fts_anything`` stores every dataset:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/   ← Data Catalog root

Each subdirectory inside is one **Dataset**, identified by its folder name.
You can have as many datasets as you want sitting side by side:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/
    ├── movie/           ← dataset "movie"
    ├── bookmarks/       ← dataset "bookmarks"
    └── terraform/       ← dataset "terraform"

Inside each dataset folder, files follow a strict naming convention based on
the dataset name. For a dataset called ``movie``:

.. code-block:: text

    ~/.alfred-afwf/afwf_fts_anything/
    └── movie/
        ├── movie-setting.json   ← search & display configuration  (you create this)
        ├── movie-data.json      ← your records as a JSON array     (you create this, or via data_url)
        ├── movie-index/         ← full-text search index           (auto-generated, do not edit)
        └── icons/
            └── movie-icon.png   ← icon files referenced by setting (optional)

The naming pattern is always ``{dataset-name}-setting.json``,
``{dataset-name}-data.json``, and ``{dataset-name}-index/``. Icons live in a
shared ``icons/`` subdirectory inside the dataset folder.

**What each file does** is covered in detail in :ref:`Setting-and-Data-File`.
To create your own dataset from scratch, see :ref:`Build-Your-Own-Dataset`.
