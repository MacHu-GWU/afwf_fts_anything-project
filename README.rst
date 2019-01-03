
.. image:: https://travis-ci.org/MacHu-GWU/afwf_fts_anything-project.svg?branch=master
    :target: https://travis-ci.org/MacHu-GWU/afwf_fts_anything-project?branch=master

.. image:: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
      :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/releases


The Alfred Workflow: Full Text Search Anything
==============================================================================

.. contents::
    :local:
    :depth: 1

.. _introduction:

Introduction
------------------------------------------------------------------------------

``fts.anything`` is an `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ allow you to **custom full-text search on your own dataset**. You can easily define **which fields you want to search**, **how you want the data to be matched** and **send the result to other workflow to process**.

How it works:

.. image:: https://user-images.githubusercontent.com/6800411/50622795-1fc45580-0ede-11e9-878c-64e2ab6292b1.gif

The Data Set (IMDB Top 3 movies, content of ``movie.json``):

.. code-block:: javascript

    [
        {
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "genres": "Drama",
            "movie_id": 1,
            "title": "The Shawshank Redemption"
        },
        {
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "genres": "Crime,Drama",
            "movie_id": 2,
            "title": "The Godfather"
        },
        {
            "description": "The early life and career of Vito Corleone in 1920s New York City is portrayed, while his son, Michael, expands and tightens his grip on the family crime syndicate.",
            "genres": "Crime,Drama",
            "movie_id": 3,
            "title": "The Godfather: Part II"
        }
    ]

Search Setting (content of ``movie-setting.json``):

.. code-block:: javascript

    {
        "columns": [ // define search mode for each field
            {
                "name": "movie_id",
                "type_is_store": true
            },
            {
                "name": "title",
                "ngram_maxsize": 10,
                "ngram_minsize": 2,
                "type_is_ngram": true
            },
            {
                "name": "description",
                "type_is_phrase": true
            },
            {
                "keyword_lowercase": true,
                "name": "genres",
                "type_is_keyword": true
            }
        ],
        "title_field": "title", // title on Alfred drop down menu
        "subtitle_field": "description", // subtitle on Alfred drop down menu
        "arg_field": "movie_id", // argument for other workflow component
        "autocomplete_field": "{movie_id} - {title}", // tab auto complete behavior
        "icon_field": "/Users/sanhehu/.alfred-fts/movie-icon.png"
    }


Note: ``fts.anything`` support comment in json.


.. _install:

Install
------------------------------------------------------------------------------
Go to `Release <https://github.com/MacHu-GWU/afwf_fts_anything-project/releases>`_, download the latest ``Full-Text-Search-Anything.alfredworkflow``. And double click to install to alfred.


Usage Guide
------------------------------------------------------------------------------

1. Create an ``.alfred-fts`` directory in your ``${HOME}`` dir (``/Users/<username>``). This is where you put your dataset file and setting file.
2. Put your data in `json <https://www.json.org/>`_ format in ``<dataname>.json``, for example, ``movie.json``. ``<dataname>`` **is the name of your dataset, use alpha letters and digits only, NO SPECIAL CHARACTER ALLOWED**, for example ``movie``, ``music``. The json content should be a list of dictionary. Each dictionary is a key-value pair mapper representing a record.
3. Define the setting file in `json <https://www.json.org/>`_ format in `<dataname>-setting.json`.
4. Custom the script filter like this, change the script to ``/usr/bin/python main.py <dataname> {query}``, the **dataname** has to match your data file name. For example ``/usr/bin/python main.py movie {query}``. You can change the **Keyword**, **Placeholder Title**, **Placeholder Subtext**, **Please Wait Subtext** as you wish.

.. image:: https://user-images.githubusercontent.com/6800411/50622686-41710d00-0edd-11e9-84d7-77a356994d4b.png

5. Make sure your run behavior is set as follow.

.. image:: https://user-images.githubusercontent.com/6800411/50622685-41710d00-0edd-11e9-9ac9-c904ed0bfd4f.png


FTS Anything Setting File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is a dictonary with 6 fields:

- ``columns``: required, list of dictionary, define search mode for each field, every sub-dictionary is a **Column Setting**.
- ``title_field``: optional, define how do you construct Title in Alfred drop down menu.
- ``subtitle_field``: optional, define how do you construct Subtitle in Alfred drop down menu.
- ``arg_field``: optional, define how do you construct Arg in Alfred drop down menu.
- ``autocomplete_field``: optional, define how do you construct Auto Complete (Tab behavior) in Alfred drop down menu.
- ``icon_field``: optional, define how do you construct Icon in Alfred drop down menu.

.. code-block:: javascript

    {
        "columns": [ // define search mode for each field
            {
                "name": "movie_id",
                "type_is_store": true
            },
            {
                "name": "title",
                "ngram_maxsize": 10,
                "ngram_minsize": 2,
                "type_is_ngram": true
            },
            {
                "name": "description",
                "type_is_phrase": true
            },
            {
                "keyword_lowercase": true,
                "name": "genres",
                "type_is_keyword": true
            }
        ],
        "title_field": "{title} ({genres})", // title on Alfred drop down menu
        "subtitle_field": "description", // subtitle on Alfred drop down menu
        "arg_field": "movie_id", // argument for other workflow component
        "autocomplete_field": "{movie_id} - {title}", // tab auto complete behavior
        "icon_field": "/Users/sanhehu/.alfred-fts/movie-icon.png"
    }

**Column Setting**:

column setting template:

.. code-block:: javascript

    {
        "name": "<field_name>", // required, text, the field name
        "type_is_store": false, // optional, boolean, true or false, default false, indicate that it is a store type field
        "type_is_ngram": false, // optional, boolean, true or false, default false, indicate that it is a ngram type field
        "type_is_phrase": false, // optional, boolean, true or false, default false, indicate that it is a phrase type field
        "type_is_keyword": false, // optional, boolean, true or false, default false, indicate that it is a keyword type field
        "ngram_minsize": 2, // optional, integer, ngram minimal character length, only used for ngram field
        "ngram_maxsize": 10, // optional, integer, ngram maximum character length, only used for ngram field
        "keyword_lowercase": true, // optional, boolean, true or false, default true, if true, then ignore case, only used for keyword field
        "keyword_commas": true // optional, boolean, true or false, default true, if true, then the keywords are separate by comma, otherwise by space
    }

**Column Type**:

- store: only stored and not searchable, usually are used for creating title / subtitle / arg / autocomplete
- `ngram <https://en.wikipedia.org/wiki/N-gram>`_: this field are indexed by several ngram token. For example: ``Hello`` will be indexed by ``he``, ``el``, ``ll``, ``lo``, ``hel``, ``ell``, ``llo``, ``hell``, ``ello``, ``hello``; if (minsize, maxsize) is (2, 5). Any token from these can match the record. For long text field, large maxsize will be very expensive.
- phrase: this field will be tokenized by words, only the full word (case insensitive) can match the record. For example: ``Alfred Workflow FTS Anything`` will be matched by ``alfred``, ``workflow``, ``fts``, ``anything``.
- keyword: thie field will be tokenized by separator, usually by comma, sometimes by space. Only the one and more full keywords can match the record. For example: ``Drama,Crime`` will be matched by ``crime``, ``drama``, ``crime drama``.

**Important**: one and only one of ``type_is_store``, ``type_is_ngram``, ``type_is_phrase``, ``type_is_keyword`` could be true for each column.

**Customize Alfred Drop Down Item**:

``title_field``, ``subtitle_field``, ``arg_field``, ``autocomplete_field``, ``icon_field`` defines how you want to construct drop down items. By default, everything is None. Let's use ``title_field`` as an example:

1. if ``title_field`` is not defined, use the ``"title"`` field in the record, this **will raise error** if ``"title"`` field not exist.
2. if ``title_field`` is a string, let's say it is ``"movie_title"``, test if it is one of columns fields, if true, then use that field (``"movie_title"``)for title.
3. if ``title_field`` is a str, but not in columns fields, it must be a `Python String Format Template <https://docs.python.org/3/library/string.html#format-examples>`_. For example: ``{movie_id} - {title}``.


FAQ
------------------------------------------------------------------------------

- Q: Why use json, why not CSV?
- A: json provides more flexibility and compatible with multi-line text, which CSV usually not.

- Q: Why it still returns old data after I updated the dataset?
- A: Just delete the ``${HOME}/.alfred-fts/<dataname>-whoosh_index`` directory.
