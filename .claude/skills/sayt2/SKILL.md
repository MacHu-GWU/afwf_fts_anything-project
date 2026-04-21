---
name: sayt2
description: Teaches how to use the sayt2 Python library to build search-as-you-type applications. Use when the user asks how to use sayt2, wants to build a search index, or needs help with sayt2 DataSet, fields, queries, sorting, or caching.
---

# sayt2 -- Search-As-You-Type Library for Python

**IMPORTANT**: This skill document is the complete API reference. Do NOT read or search for local sayt2 source files. Everything you need is in this document. If you truly need to inspect the implementation, fetch from GitHub:

- Source tree: https://github.com/MacHu-GWU/sayt2-project/tree/main/sayt2
- Single file (example): https://raw.githubusercontent.com/MacHu-GWU/sayt2-project/refs/heads/main/sayt2/dataset.py

## Overview

**sayt2** is a Python library that lets you build a full-text search index from a list of dictionaries and query it with substring matching (ngram), BM25 full-text search, fuzzy search, range queries, sorting, and more -- all through a single `DataSet` object.

Under the hood it uses [tantivy](https://github.com/quickwit-oss/tantivy-py) (Rust-based search engine), [pydantic](https://docs.pydantic.dev/) for validation, and [diskcache](https://grantjenks.com/docs/diskcache/) for a two-layer disk cache.

## Installation

```bash
pip install sayt2
```

## Import Convention

```python
# Option A: import specific names
from sayt2.api import (
    # --- Field types ---
    BaseField,
    StoredField,
    KeywordField,
    TextField,
    NgramField,
    NumericField,
    DatetimeField,
    BooleanField,
    T_Field,            # discriminated union type of all field types
    fields_schema_hash, # deterministic hash of a list of field definitions
    # --- Dataset, search result, sort ---
    DataSet,
    SortKey,
    Hit,
    SearchResult,
    # --- Cache and tracker ---
    DataSetCache,
    Tracker,
    # --- Constants ---
    FieldTypeEnum,      # "stored", "keyword", "text", "ngram", "numeric", "datetime", "boolean"
    TokenizerEnum,      # "default", "en_stem"
    NumericKindEnum,    # "i64", "u64", "f64"
    # --- Exceptions ---
    MalformedFieldSettingError,
    MalformedDatasetSettingError,
    TrackerIsLockedError,
)

# Option B: import the module
import sayt2.api as sayt2
# then use sayt2.DataSet, sayt2.NgramField, etc.
```

---

## Complete API Reference

### Field Types

Fields tell sayt2 how to index each column in your data. All fields inherit from `BaseField`.

#### BaseField (base class)

All field types share these attributes:

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required, min_length=1) | Column name in your data dicts |
| `stored` | `bool` | `True` | Whether to store the value (returned in search results) |

#### StoredField

Store-only field. Not indexed, not searchable, not sortable. Use for extra metadata you want returned in results.

```python
StoredField(name="metadata")
```

#### KeywordField

Exact-match field. Uses `raw` tokenizer -- the entire field value is one token.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `boost` | `float` | `1.0` | Ranking weight multiplier (must be > 0) |

```python
KeywordField(name="id")
KeywordField(name="tag", boost=2.0)
```

#### TextField

Full-text BM25 word-level search field.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `tokenizer` | `"default"` or `"en_stem"` | `"default"` | `"default"` = Unicode word boundary; `"en_stem"` = English stemming |
| `boost` | `float` | `1.0` | Ranking weight multiplier (must be > 0) |

```python
TextField(name="bio")
TextField(name="description", tokenizer="en_stem", boost=2.0)
```

#### NgramField

Search-as-you-type field. Builds an ngram inverted index so that any substring of length `[min_gram, max_gram]` is a valid query token.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `min_gram` | `int` | `2` | Minimum ngram length (>= 1) |
| `max_gram` | `int` | `6` | Maximum ngram length (>= min_gram) |
| `prefix_only` | `bool` | `False` | If True, only generate prefix ngrams |
| `lowercase` | `bool` | `True` | If True, apply lowercase filter |
| `boost` | `float` | `1.0` | Ranking weight multiplier (must be > 0) |

```python
NgramField(name="name", min_gram=2, max_gram=6, boost=3.0)
NgramField(name="title", min_gram=3, max_gram=8, prefix_only=True)
```

#### NumericField

Numeric values for range queries and sorting.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `kind` | `"i64"`, `"u64"`, or `"f64"` | `"i64"` | Integer, unsigned integer, or float |
| `indexed` | `bool` | `False` | Enable range queries (e.g. `year:[2020 TO 2025]`) |
| `fast` | `bool` | `True` | Enable sorting |

```python
NumericField(name="year", kind="i64", indexed=True, fast=True)
NumericField(name="price", kind="f64", indexed=True, fast=True)
NumericField(name="rating", kind="f64")  # sort-only by default
```

#### DatetimeField

Datetime field backed by tantivy's date type.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `indexed` | `bool` | `True` | Enable range queries |
| `fast` | `bool` | `True` | Enable sorting |

```python
DatetimeField(name="created_at")
```

#### BooleanField

Boolean field for true/false values.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name |
| `stored` | `bool` | `True` | Store in results |
| `indexed` | `bool` | `True` | Enable filtering |

```python
BooleanField(name="active")
```

#### T_Field

A pydantic discriminated union of all field types. Use with `TypeAdapter` for polymorphic deserialization:

```python
from pydantic import TypeAdapter
from sayt2.api import T_Field

adapter = TypeAdapter(T_Field)
field = adapter.validate_python({"type": "ngram", "name": "title"})
```

#### fields_schema_hash(fields: list[T_Field]) -> str

Returns a deterministic 16-char hex hash of a list of field definitions. Used internally as part of cache keys so that changing the schema automatically invalidates stale caches.

---

### SortKey

One element of a multi-field sort specification.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Field name to sort by |
| `descending` | `bool` | `True` | Sort direction |

```python
SortKey(name="rating", descending=True)
SortKey(name="year", descending=False)
```

---

### Hit

A single search hit (frozen dataclass).

| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | `dict[str, Any]` | The original document dict (stored fields only) |
| `score` | `float` | Relevance score |

---

### SearchResult

Immutable search result (frozen dataclass) returned by `DataSet.search()`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `hits` | `list[Hit]` | List of search hits |
| `size` | `int` | Number of results |
| `took_ms` | `int` | Search time in milliseconds |
| `fresh` | `bool` | True if the index was just rebuilt |
| `cache` | `bool` | True if served from cache |

**Methods:**

- `to_json() -> str`: Serialize to pretty-printed JSON string.
- `jprint()`: Print the JSON representation to stdout.

---

### DataSet

The main entry point. Manages indexing, searching, and caching. It is a pydantic `BaseModel`.

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dir_root` | `Path` | (required) | Root directory for index, cache, and tracker files |
| `name` | `str` | (required) | Unique logical name for this dataset |
| `fields` | `list[T_Field]` | (required) | List of field definitions |
| `downloader` | `Callable[[], Iterable[dict]]` or `None` | `None` | Callable that returns your data |
| `cache_expire` | `int` or `None` | `None` | Seconds before cache expires (`None` = never) |
| `sort` | `list[SortKey]` or `None` | `None` | Default sort specification |
| `memory_budget_bytes` | `int` | `128_000_000` | Heap budget for the tantivy index writer |
| `num_threads` | `int` or `None` | `None` | Number of indexing threads (`None` = tantivy default) |
| `lock_expire` | `int` | `60` | Seconds before the cross-process tracker lock expires |

#### Methods

##### `search(query: str, limit: int = 20, refresh: bool = False) -> SearchResult`

Full search flow:
1. Check data freshness (or `refresh=True` forces rebuild).
2. If stale, calls `build_index()` with the configured `downloader`.
3. Check query cache.
4. On cache miss, execute the query, apply sorting, cache the result.

The `query` parameter uses **Lucene query syntax** (from tantivy):
- Simple text: `"alice"` -- matches all searchable fields
- Field-specific: `"author:blandy"` -- matches a specific field
- Range queries: `"year:[2020 TO 2025]"`, `"price:>40"`, `"price:[10 TO 50]"`
- Boolean operators: `"python AND year:[2022 TO 2025]"`, `"python OR rust"`

##### `build_index(data: Iterable[dict] | None = None) -> int`

Build or rebuild the index with cross-process lock protection. If `data` is `None`, the `downloader` is called. Returns the number of documents indexed.

##### `close() -> None`

Close the underlying cache (sqlite3 connection). Safe to call multiple times.

##### Context Manager Support

```python
with DataSet(...) as ds:
    result = ds.search("query")
# ds.close() is called automatically
```

---

### DataSetCache

Two-layer disk cache backed by `diskcache`. Usually managed internally by `DataSet`, but can be used directly for advanced use cases.

**Constructor:** `DataSetCache(dir_cache: Path, dataset_name: str, schema_hash: str, expire: int | None = None)`

**Methods:**

| Method | Description |
|--------|-------------|
| `is_fresh() -> bool` | True if the dataset index is still considered fresh |
| `mark_fresh()` | Mark dataset as fresh, starts L1 expiry countdown |
| `get_query_result(query, limit) -> SearchResult or None` | Get cached query result (None = miss) |
| `set_query_result(query, limit, result)` | Cache a query result |
| `evict_all()` | Remove all entries (L1 + L2) for this dataset |
| `close()` | Close the underlying diskcache |

---

### Tracker

SQLite-backed cross-process lock manager. Usually managed internally by `DataSet`, but can be used directly for advanced use cases.

**Constructor:** `Tracker(db_path: Path)`

**Methods:**

| Method | Description |
|--------|-------------|
| `lock_it(name, expire=60) -> str` | Acquire lock atomically, returns lock token. Raises `TrackerIsLockedError` if held. |
| `unlock_it(name, lock_token)` | Release lock (only if token matches). Silent no-op if token mismatch. |
| `lock(name, expire=60)` | Context manager that acquires on entry, releases on exit. |

```python
tracker = Tracker(db_path)
with tracker.lock("books", expire=60):
    # safe to rebuild index
    ...
```

---

### Exceptions

| Exception | Base | Description |
|-----------|------|-------------|
| `MalformedFieldSettingError` | `ValueError` | Invalid field configuration |
| `MalformedDatasetSettingError` | `ValueError` | Invalid DataSet configuration (e.g. duplicate field names) |
| `TrackerIsLockedError` | `RuntimeError` | Lock is held by another process |

---

### Constants (Enums)

All are `str` enums (can be used as plain strings).

| Enum | Values |
|------|--------|
| `FieldTypeEnum` | `"stored"`, `"keyword"`, `"text"`, `"ngram"`, `"numeric"`, `"datetime"`, `"boolean"` |
| `TokenizerEnum` | `"default"`, `"en_stem"` |
| `NumericKindEnum` | `"i64"`, `"u64"`, `"f64"` |

---

## Example 1 -- People Directory (Ngram + Full-Text Search)

### Step 1: Prepare the data

```python
records = [
    {
        "id": "1",
        "name": "Alice Johnson",
        "title": "Senior Data Scientist",
        "bio": "Alice specializes in machine learning and natural language processing.",
    },
    {
        "id": "2",
        "name": "Bob Martinez",
        "title": "Backend Engineer",
        "bio": "Bob builds scalable microservices with Python and Go.",
    },
    {
        "id": "3",
        "name": "Charlie Wang",
        "title": "Frontend Developer",
        "bio": "Charlie creates beautiful user interfaces with React and TypeScript.",
    },
    {
        "id": "4",
        "name": "Diana Patel",
        "title": "DevOps Engineer",
        "bio": "Diana manages cloud infrastructure on AWS and Kubernetes.",
    },
    {
        "id": "5",
        "name": "Edward Kim",
        "title": "Machine Learning Engineer",
        "bio": "Edward trains and deploys deep learning models for computer vision.",
    },
]
```

### Step 2: Define the schema

```python
from sayt2.api import DataSet, NgramField, TextField, KeywordField

fields = [
    KeywordField(name="id"),
    NgramField(name="name", min_gram=2, max_gram=6, boost=3.0),
    TextField(name="title", boost=2.0),
    TextField(name="bio"),
]
```

### Step 3: Create the DataSet and search

```python
from pathlib import Path
import shutil

dir_index = Path("./my_search_index")
if dir_index.exists():
    shutil.rmtree(dir_index)

def downloader() -> list[dict]:
    """Return the raw records. In real use this could hit a DB or API."""
    return records
```

**Option A -- context manager (recommended):**

`DataSet` supports `with` statement, which automatically closes the index and cache when the block exits.

```python
with DataSet(
    dir_root=dir_index,
    name="people",
    fields=fields,
    downloader=downloader,
    cache_expire=None,
) as ds:
    # Ngram search -- substring matching (search-as-you-type)
    result = ds.search("ali")
    # Returns Alice Johnson
    for hit in result.hits:
        print(f"{hit.source['name']} (score: {hit.score:.2f})")

    # Full-text search -- BM25 word-level
    result = ds.search("machine learning")
    # Returns Edward Kim, Alice Johnson

    # Check cache behavior
    r1 = ds.search("kubernetes")     # cache miss
    r2 = ds.search("kubernetes")     # cache hit (r2.cache == True)

    # Force rebuild the index
    r = ds.search("kubernetes", refresh=True)  # r.fresh == True
# ds is automatically closed here
```

**Option B -- manual close:**

If you cannot use a `with` block, call `ds.close()` explicitly when done.

```python
ds = DataSet(
    dir_root=dir_index,
    name="people",
    fields=fields,
    downloader=downloader,
    cache_expire=None,
)

result = ds.search("ali")
for hit in result.hits:
    print(f"{hit.source['name']} (score: {hit.score:.2f})")

# Always close when done
ds.close()
```

## Example 2 -- Book Catalog (Sort + Range Queries)

### Step 1: Define schema with NumericFields

```python
from sayt2.api import DataSet, NgramField, TextField, KeywordField, NumericField, SortKey

book_fields = [
    KeywordField(name="id"),
    NgramField(name="title", min_gram=2, max_gram=6, boost=3.0),
    TextField(name="author", boost=2.0),
    TextField(name="description"),
    NumericField(name="year", kind="i64", indexed=True, fast=True),
    NumericField(name="price", kind="f64", indexed=True, fast=True),
    NumericField(name="rating", kind="f64", indexed=True, fast=True),
]
```

### Step 2: Create DataSet with sorting

```python
books = [
    {"id": "1", "title": "Fluent Python", "author": "Luciano Ramalho",
     "description": "A guide to writing effective Python code.",
     "year": 2022, "price": 49.99, "rating": 4.7},
    {"id": "2", "title": "Python Crash Course", "author": "Eric Matthes",
     "description": "A fast-paced introduction to programming with Python.",
     "year": 2023, "price": 35.99, "rating": 4.6},
    {"id": "3", "title": "Programming Rust", "author": "Jim Blandy",
     "description": "Fast, safe systems development with Rust.",
     "year": 2021, "price": 45.99, "rating": 4.5},
]

with DataSet(
    dir_root=Path("./book_index"),
    name="books",
    fields=book_fields,
    downloader=lambda: books,
    sort=[SortKey(name="rating", descending=True)],
) as ds:
    # Sort by rating (highest first)
    result = ds.search("python")

    # Range queries (Lucene syntax)
    result = ds.search("year:[2020 TO 2023]")
    result = ds.search("price:>40")

    # Field-specific search
    result = ds.search("author:blandy")

    # Boolean operators
    result = ds.search("python AND year:[2022 TO 2025]")
```

## Quick Reference

| Feature | How to use |
|---------|-----------|
| Substring search (search-as-you-type) | `NgramField` + `ds.search("ali")` |
| Full-text search | `TextField` + `ds.search("machine learning")` |
| Full-text with English stemming | `TextField(tokenizer="en_stem")` |
| Exact match | `KeywordField` |
| Sort results | `SortKey(name="rating", descending=True)` |
| Range query | `ds.search("year:[2020 TO 2025]")` or `ds.search("price:>40")` |
| Field-specific search | `ds.search("author:blandy")` |
| Boolean operators | `ds.search("python AND year:[2020 TO 2025]")` |
| Force refresh | `ds.search("query", refresh=True)` |
| Automatic caching | Built-in, no config needed |
| Build index manually | `ds.build_index(data=my_records)` |
| Pretty-print results | `result.jprint()` |

## Common Patterns

### Data from a database or API

```python
import json
import requests

def downloader() -> list[dict]:
    resp = requests.get("https://api.example.com/items")
    return resp.json()

# Or from a local JSON file
def downloader() -> list[dict]:
    with open("data.json") as f:
        return json.load(f)
```

### Refreshing the index when data changes

```python
# Normal search -- uses cached index
result = ds.search("query")

# Force rebuild -- re-downloads data and rebuilds index
result = ds.search("query", refresh=True)
```

### Iterating over results

```python
result = ds.search("python")
print(f"Found {result.size} results in {result.took_ms:.1f}ms")
for hit in result.hits:
    print(f"  [{hit.score:.2f}] {hit.source['title']}")
```

### Building the index separately from searching

```python
# Build index with explicit data (no downloader needed)
ds = DataSet(
    dir_root=Path("./index"),
    name="mydata",
    fields=fields,
)
count = ds.build_index(data=my_records)
print(f"Indexed {count} documents")

# Later, search (no downloader needed if data is already indexed and fresh)
result = ds.search("query")
```

For full documentation, see https://sayt2.readthedocs.io/
