#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test handler using real data in $HOME/.alfred-fts/

content of ``$HOME/.alfred-fts/movie.json``:

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
            "genres": "Crime, Drama",
            "movie_id": 2,
            "title": "The Godfather"
        },
        {
            "description": "The early life and career of Vito Corleone in 1920s New York City is portrayed, while his son, Michael, expands and tightens his grip on the family crime syndicate.",
            "genres": "Crime, Drama",
            "movie_id": 3,
            "title": "The Godfather: Part II"
        }
    ]

content of ``$HOME/.alfred-fts/movie-setting.json``:

.. code-block:: javascript

    {
        "arg_field": "movie_id",
        "autocomplete_field": "{movie_id} - {title}",
        "columns": [
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
        "subtitle_field": "description",
        "title_field": "{title} ({genres})"
    }
"""

import pytest
from workflow import Workflow3
from afwf_fts_anything.handlers import handler
from afwf_fts_anything.handlers import MSG_FOUND_NOTHING


class TestSearch(object):
    def test_no_argument(self):
        wf = Workflow3()
        handler(wf, args=["movie"])
        assert len(wf._items) == 1
        item = wf._items[0]
        assert "Search in Dataset" in item.title

    def test_found_nothing(self):
        wf = Workflow3()
        handler(wf, args=["movie", "YouCanNotFindMe"])
        assert len(wf._items) == 1
        item = wf._items[0]
        assert item.title == MSG_FOUND_NOTHING

    def test_found(self):
        wf = Workflow3()
        handler(wf, args=["movie", "redempt"]) # match the ngram 'title' field
        assert len(wf._items) == 1
        assert wf._items[0].title == "The Shawshank Redemption (Drama)"
        assert wf._items[0].arg == "1"
        assert wf._items[0].autocomplete == "The Shawshank Redemption"

        wf = Workflow3()
        handler(wf, args=["movie", "father"]) # match the ngram 'title' field
        assert len(wf._items) == 2
        for item in wf._items:
            assert "The Godfather" in item.title

        wf = Workflow3()
        handler(wf, args=["movie", "EMPIRE"]) # match the phrase 'descrpition' field
        assert len(wf._items) == 1
        assert wf._items[0].title == "The Godfather (Crime, Drama)"

        wf = Workflow3()
        handler(wf, args=["movie", "transfers", "control"])  # match the phrase 'descrpition' field
        assert len(wf._items) == 1
        assert wf._items[0].title == "The Godfather (Crime, Drama)"
        assert wf._items[0].arg == "2"
        assert wf._items[0].autocomplete == "The Godfather"

        wf = Workflow3()
        handler(wf, args=["movie", "empi"])  # match the phrase 'descrpition' field
        assert len(wf._items) == 1
        assert wf._items[0].title == "Found Nothing"

        wf = Workflow3()
        handler(wf, args=["movie", "family"])  # match the phrase 'descrpition' field
        assert len(wf._items) == 1
        assert wf._items[0].title == "The Godfather: Part II (Crime, Drama)"

        wf = Workflow3()
        handler(wf, args=["movie", "Drama", "Crime"])  # match the keyword 'genres' field
        assert len(wf._items) == 2
        for item in wf._items:
            assert "The Godfather" in item.title

        wf = Workflow3()
        handler(wf, args=["movie", "drama"])
        assert len(wf._items) == 3


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
