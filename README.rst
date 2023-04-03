.. image:: https://github.com/MacHu-GWU/afwf_fts_anything-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/afwf_fts_anything-project

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

------

.. .. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://github.com/MacHu-GWU/afwf_fts_anything-project

.. .. image:: https://img.shields.io/badge/Link-Install-blue.svg
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


Introduction
------------------------------------------------------------------------------
``afwf_fts_anything`` is an `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ allows you to do full-text search on your own dataset, and use the result to open url, open file, run script, or basically do anything. Typically, you need to setup expansive `elasticsearch <https://github.com/elastic/elasticsearch>`_ server, learn how to do data ingestion, learn search API, and build your own Alfred workflow. ``afwf_fts_anything`` removes all the blockers and let you just focus on your dataset and search configuration.

**Demo**

.. image:: https://user-images.githubusercontent.com/6800411/50622795-1fc45580-0ede-11e9-878c-64e2ab6292b1.gif

Sample Data Set, IMDB Top 250 movies (content of ``movie.json``):

.. code-block:: javascript

      [
          {
              "movie_id": 1,
              "title": "The Shawshank Redemption",
              "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
              "genres": "Drama",
              "rating": 9.2
          },
          {
              "movie_id": 2,
              "title": "The Godfather",
              "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
              "genres": "Crime, Drama",
              "rating": 9.2
          },
          {
              "movie_id": 3,
              "title": "The Dark Knight",
              "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
              "genres": "Action, Crime, Drama",
              "rating": 9.0
          },
          {
              "movie_id": 4,
              "title": "12 Angry Men",
              "description": "The jury in a New York City murder trial is frustrated by a single member whose skeptical caution forces them to more carefully consider the evidence before jumping to a hasty verdict.",
              "genres": "Crime, Drama",
              "rating": 9.0
          },
          {
              "movie_id": 5,
              "title": "Schindler's List",
              "description": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
              "genres": "Biography, Drama, History",
              "rating": 8.9
          },
          {
              "movie_id": 6,
              "title": "The Lord of the Rings: The Return of the King",
              "description": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.",
              "genres": "Action, Adventure, Drama",
              "rating": 8.9
          },
          {
              "movie_id": 7,
              "title": "Pulp Fiction",
              "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
              "genres": "Crime, Drama",
              "rating": 8.8
          },
          {
              "movie_id": 8,
              "title": "Fight Club",
              "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
              "genres": "Drama",
              "rating": 8.7
          },
          {
              "movie_id": 9,
              "title": "Saving Private Ryan",
              "description": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.",
              "genres": "Drama, War",
              "rating": 8.6
          }
      ]

Sample search settings (content of ``movie-setting.json``):

.. code-block:: javascript

      {
          // define how you want to search this dataset
          "fields": [
              {
                  "name": "movie_id",
                  "type_is_store": true
              },
              {
                  "name": "title",
                  "type_is_store": true,
                  "type_is_ngram": true,
                  "ngram_maxsize": 10,
                  "ngram_minsize": 2,
                  "weight": 2.0
              },
              {
                  "name": "description",
                  "type_is_store": true,
                  "type_is_phrase": true
              },
              {
                  "name": "genres",
                  "type_is_store": true,
                  "type_is_keyword": true,
                  "keyword_lowercase": true,
                  "weight": 1.5
              },
              {
                  "name": "rating",
                  "type_is_store": true,
                  "type_is_numeric": true,
                  "is_sortable": true,
                  "is_sort_ascending": false
              }
          ],
          "title_field": "{title} ({genres}) rate {rating}", // title on Alfred drop down menu
          "subtitle_field": "{description}", // subtitle on Alfred drop down menu
          "arg_field": "{movie_id}", // argument for other workflow component
          "autocomplete_field": "{title}", // tab auto complete behavior
          "icon_field": "movie-icon.png"
      }

Note:

      ``afwf_fts_anything`` support comments in json, you don't have to remove it to use.
