.. _release_history:

Release and Version History
==============================================================================


Backlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


1.2.1 (2024-01-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``ngram_words`` index type. It tokenizes the text into words before index. It is more accurate than ``ngram`` if you have delimiter in your text.

**Minor Improvements**

- Fix a bug that it also open the url even it is not a valid url item.


1.1.1 (2023-04-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First API stable release.
- drop support for Python2.7.
- only support for Python3.7+.
- adapt `afwf <https://github.com/MacHu-GWU/afwf-project>`_ framework 0.3.1.
- allow field boost for search result sorting by weight.
- allow sortable field for custom result sorting.
- allow custom icon.
- allow download ``.json`` or ``.json.zip`` data file from internet.
- add ``?`` to search query to get help message.

**Minor Improvements**

- reword the user document.


0.0.3 (2021-07-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- Support the End of life Python2.7


0.0.2 (2020-05-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Allow column specified index search settings


0.0.1 (2019-01-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release!
- support ngram, phrase, keyword search.
- easy to custom workflow item.
