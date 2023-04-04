How to Use
==============================================================================


Installation
------------------------------------------------------------------------------
- Make sure you have installed `Alfred 3+ <https://www.alfredapp.com/>`_.
- Make sure you already purchased `Powerpack <https://www.alfredapp.com/powerpack/>`_, you have to buy powerpack to use `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ feature.
- Go to `Release <https://github.com/MacHu-GWU/afwf_fts_anything-project/releases>`_, download the latest ``afwf_fts_anything-${version}-macosx_universal.alfredworkflow
``. And double click to import to Alfred Workflow. Since this project only uses pure Python library (no C library), so it is universal for both Intel and ARM MacOS.


Test with The Sample Movie Dataset
------------------------------------------------------------------------------
- Go to `Release <https://github.com/MacHu-GWU/afwf_fts_anything-project/releases>`_. Find the latest release.
- Download the ``movie.zip`` and uncompress it at ``${HOME}/.alfred-afwf/afwf_fts_anything/``. You should see:
    - ``${HOME}/.alfred-afwf/afwf_fts_anything/movie-setting.json``
    - ``${HOME}/.alfred-afwf/afwf_fts_anything/movie-data.json``
    - ``${HOME}/.alfred-afwf/afwf_fts_anything/movie-icon/``
- Type ``fts movie god father`` or ``fts movie drama`` in Alfred input box. The first command may fail because it takes time to build the index. The second command should work.


Bring your own Dataset
------------------------------------------------------------------------------
- Make sure you understand `How it Works <./01-How-it-Works.rst>`_.
- Give your dataset a name. Let's say it is ``mydata``.
- Put your setting file at ``${HOME}/.alfred-afwf/afwf_fts_anything/mydata-setting.json``.
- Put your data file at ``${HOME}/.alfred-afwf/afwf_fts_anything/mydata-data.json``.
- Copy and paste the existing ``fts movie`` Script Filter, update the configuration accordingly. You must update the ``Keyword`` and update the dataset name in the ``Script``.
- Type ``fts mydata your_query_here`` in Alfred input to search.


FAQ
------------------------------------------------------------------------------
- Q: Why use json, why not CSV?
- A: json provides more flexibility and compatible with multi-line text, which CSV usually not.

- Q: Why it still returns old data after I updated the dataset?
- A: Just delete the ``${HOME}/.alfred-afwf/afwf_fts_anything/<dataset_name>-whoosh_index`` directory.
