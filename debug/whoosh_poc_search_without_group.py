# -*- coding: utf-8 -*-

import typing as T
from pathlib_mate import Path
from whoosh import fields
from whoosh import index, qparser


dir_here = Path.dir_here(__file__)
dir_index = dir_here / ".index"


class Schema(fields.SchemaClass):
    """
    Define whoosh schema.
    """

    id = fields.ID(stored=True)
    name = fields.NGRAM(minsize=2, maxsize=10, stored=True)
    description = fields.TEXT(stored=True)
    tags = fields.KEYWORD(lowercase=True, stored=True)


def remove_index():
    dir_index.remove_if_exists()


def get_index() -> index.FileIndex:
    if dir_index.exists():
        return index.open_dir(dir_index.abspath)
    else:
        schema = Schema()
        dir_index.mkdir_if_not_exists()
        return index.create_in(dirname=dir_index.abspath, schema=schema)


def rebuild_index():
    remove_index()

    dataset = [
        dict(
            id="employee-1",
            name="Michelle Castillo",
            description="The feminine form of Michael",
            tags="HR",
        ),
        dict(
            id="employee-1",
            name="Fletcher Carpenter",
            description="A maker of arrows",
            tags="IT",
        ),
        dict(
            id="employee-3",
            name="Jewel Davidson",
            description="A precious gem",
            tags="Finance",
        ),
    ]
    idx = get_index()
    writer = idx.writer()
    for doc in dataset:
        writer.add_document(**doc)
    writer.commit()


def search(query_str: str, limit=5):
    """
    Perform full-text search for result.
    """
    schema = Schema()
    idx = get_index()
    query = qparser.MultifieldParser(
        ["name", "description", "tags"],
        schema=schema,
    ).parse(query_str)

    with idx.searcher() as searcher:
        result = [hit.fields() for hit in searcher.search(query, limit=limit)]
        print(result)
    return result


# rebuild_index()
search("jewel")
