---
name: afwf
description: Guide for building Alfred workflow Python packages using the afwf SDK. Use when creating, modifying, or debugging afwf-based Alfred workflows — Script Filters, CLI entry points, fuzzy matching, disk caching, write actions, testing, or deployment.
---

# afwf — Alfred Workflow Python SDK

`afwf` is a Python SDK for building Alfred Script Filter workflows. The core idea: write Python functions that return a `ScriptFilter` object, expose them as a CLI via `fire`, call the CLI from Alfred's Script field. **Do NOT search the source repo** — this skill is the complete reference.

---

## Architecture: Three Layers

```
Layer 1 — Python logic (my_pkg/your_module.py)
  Your package name is whatever you choose (e.g. my_pkg, my_workflow_pkg).
  afwf is the SDK you import — not your package name.
  Pure functions: main(query: str) → ScriptFilter. No Alfred dependency. Unit-testable.

Layer 2 — CLI entry point (my_pkg/cli.py → declared as console_script)
  fire.Fire(Command) exposes each main() as a subcommand.
  Alfred's Script field calls this binary.

Layer 3 — Alfred workflow config (info.plist)
  Keywords, Script Filter nodes, Conditional branches, action widgets.
  Static — never changes when Python logic changes.
```

**`pyproject.toml`** declares the entry point:
```toml
[project.scripts]
my-workflow = "my_pkg.cli:main"
```

**`my_pkg/cli.py`**:
```python
import fire
from my_pkg import search_items, write_item

class Command:
    def search_items(self, query: str = ""):
        search_items.main(query=query).send_feedback()

    def write_item_request(self, content: str):
        # Called by Alfred's Run Script widget — NOT a Script Filter
        write_item.write_request(content)

def main():
    fire.Fire(Command)
```

Alfred Script field (dev): `.venv/bin/my-workflow search-items --query '{query}'`
Alfred Script field (prod): `~/.local/bin/uvx --from my-pkg==1.0.0 my-workflow search-items --query '{query}'`

---

## Complete Import Map

Everything from `afwf` comes through `afwf.api`. Never import from sub-modules directly.

```python
# All core classes and utilities — use this single import
import afwf.api as afwf

# What afwf.api exports:
# afwf.ScriptFilter      — top-level response object
# afwf.Item              — one dropdown row
# afwf.Icon              — icon object
# afwf.Text              — copy/largetype text object
# afwf.IconFileEnum      — bundled PNG icon paths
# afwf.Query             — parsed query object
# afwf.QueryParser       — query tokenizer
# afwf.log_error         — error-logging decorator
# afwf.path_enum         — path helper (path_enum.dir_afwf = ~/.alfred-afwf/)
# afwf.IconTypeEnum      — "fileicon" / "filetype" constants
# afwf.ItemTypeEnum      — "default" / "file" / "file:skipcheck" constants
# afwf.ModEnum           — modifier key constants
# afwf.VarKeyEnum        — variable key name constants (internal use)
# afwf.VarValueEnum      — variable value constants (internal use)
```

Optional extras have their own import paths (NOT through `afwf.api`):
```python
import afwf.opt.fuzzy_item.api as fuzzy_item  # requires afwf[fuzzy]
from afwf.opt.fuzzy.api import FuzzyMatcher    # requires afwf[fuzzy]
from afwf.opt.cache.api import TypedCache      # requires afwf[cache]
```

---

## Core Classes

### ScriptFilter

```python
import afwf.api as afwf

sf = afwf.ScriptFilter()          # items=[] by default
sf.items.append(item)
sf.send_feedback()                 # dumps JSON to stdout; Alfred reads it
# or: afwf.ScriptFilter(items=[item1, item2]).send_feedback()
```

Fields: `items: list[Item]`

### Item

```python
item = afwf.Item(
    title="My Result",            # required — the main line
    subtitle="Details here",      # optional — second line
    arg=None,                     # str — passed to downstream widgets
    autocomplete=None,            # str — filled in search field on Tab
    match=None,                   # str — Alfred uses this for client-side filtering
    valid=True,                   # bool — False = pressing Enter does nothing
    uid=None,                     # str — Alfred learns from this for sorting
    type=None,                    # str — "default" / "file" / "file:skipcheck"
    icon=None,                    # Icon object
    text=None,                    # Text object
    quicklookurl=None,            # str — URL/path shown on Shift or ⌘Y
    mods=None,                    # dict — modifier key overrides
    variables={},                 # dict — passed to downstream Alfred widgets
)
```

`Item` methods (all return `self` for chaining):
- `set_icon(path: str)` — set icon from image file path
- `set_modifier(mod, subtitle, arg, valid)` — add modifier key override
- `open_url(url: str)` — set variables for Open URL action
- `open_file(path: str)` — set variables for Open File action
- `launch_app_or_file(path: str)` — set variables for Launch App/File action
- `reveal_file_in_finder(path: str)` — set variables for Reveal in Finder action
- `browse_in_terminal(path: str)` — set variables for Browse in Terminal action
- `browse_in_alfred(path: str)` — set variables for Browse in Alfred action
- `run_script(cmd: str)` — set variables + `item.arg` for Run Script action
- `terminal_command(cmd: str)` — set variables + `item.arg` for Terminal Command action
- `send_notification(title: str, subtitle: str = "")` — set variables for Post Notification

### Icon

```python
# From a bundled icon (most common):
item.icon = afwf.Icon(path=afwf.IconFileEnum.error)

# From a local image file (no type needed):
item.icon = afwf.Icon(path="/absolute/path/to/icon.png")

# Use the file's system icon (e.g. folder icon for ~/Desktop):
item.icon = afwf.Icon(path="~/Desktop", type="fileicon")

# Use a UTI file type icon:
item.icon = afwf.Icon(path="com.apple.rtfd", type="filetype")
```

Fields: `path: str`, `type: str | None` (`None` = treat path as image file)

### Text

```python
item.text = afwf.Text(
    copy_text="text copied with ⌘C",   # Python field name is copy_text (Alfred key: "copy")
    largetype="text shown with ⌘L",
)
```

Fields: `copy_text: str | None` (alias `"copy"`), `largetype: str | None`

### IconFileEnum — Complete List of Bundled Icons

All values are absolute paths to PNG files bundled with `afwf`:

```python
from afwf.api import IconFileEnum  # or: afwf.IconFileEnum

# Common
IconFileEnum.error       # red X — use for error/failure states
IconFileEnum.info        # info bubble
IconFileEnum.question    # question mark
IconFileEnum.search      # magnifying glass
IconFileEnum.check       # checkmark
IconFileEnum.close       # X close
IconFileEnum.gear        # settings gear
IconFileEnum.refresh     # refresh arrows
IconFileEnum.star        # star / favorite
IconFileEnum.bookmark    # bookmark

# Files & folders
IconFileEnum.folder
IconFileEnum.file
IconFileEnum.archive_folder
IconFileEnum.desktop
IconFileEnum.download
IconFileEnum.upload
IconFileEnum.trash

# Actions
IconFileEnum.plus
IconFileEnum.minus
IconFileEnum.remove
IconFileEnum.redo
IconFileEnum.undo
IconFileEnum.reset
IconFileEnum.start
IconFileEnum.stop
IconFileEnum.pause
IconFileEnum.rocket

# Development
IconFileEnum.code
IconFileEnum.console
IconFileEnum.bash
IconFileEnum.debug
IconFileEnum.git
IconFileEnum.flask

# Communication
IconFileEnum.chat
IconFileEnum.groupchat
IconFileEnum.mail
IconFileEnum.message
IconFileEnum.landline
IconFileEnum.meeting

# Devices
IconFileEnum.laptop
IconFileEnum.desktop      # (also under Files above)
IconFileEnum.iphone
IconFileEnum.android

# Other
IconFileEnum.calendar
IconFileEnum.id_card
IconFileEnum.idea
IconFileEnum.internet
IconFileEnum.password
IconFileEnum.box
IconFileEnum.fire
IconFileEnum.explosion
IconFileEnum.task
IconFileEnum.todo
IconFileEnum.dictionary
IconFileEnum.microsoft_excel
IconFileEnum.microsoft_powerpoint
IconFileEnum.microsoft_word
```

---

## Serialization Rules

`item.to_script_filter()` is called internally by `send_feedback()`. Rules differ from plain `model_dump()`:

| Python value | Output |
|---|---|
| `None` | Field **omitted** — Alfred uses its default |
| `False` / `0` / `""` | **Preserved** — e.g. `valid=False` must appear in JSON |
| Nested `ScriptFilterObject` that serializes to `{}` | Field **omitted** |
| Top-level `dict` that is `{}` | Field **omitted** (e.g. empty `variables`) |
| `dict` nested inside another `dict` (e.g. in `mods`) | **Passed through** unchanged |
| `list` (any length, including `[]`) | **Always preserved** — `items: []` is required |

You never call `to_script_filter()` directly. Just build objects and call `send_feedback()`.

---

## Item Actions — Conditional Widget Pattern

Each `item.set_*` / `item.action_*` helper writes a **flag variable** (`"y"`) + **payload variable**. Alfred's Conditional widget reads the flag and routes to the correct downstream widget. Set up the Conditional widget **once** in Alfred's UI; it covers all Script Filters.

```python
item.open_url("https://example.com")
# variables: {"open_url": "y", "open_url_arg": "https://example.com"}

item.open_file(path="/path/to/file.py")
# variables: {"open_file": "y", "open_file_path": "/path/to/file.py"}

item.launch_app_or_file(path="/Applications/Safari.app")
# variables: {"launch_app_or_file": "y", "launch_app_or_file_path": "..."}

item.reveal_file_in_finder(path="/path/to/file")
# variables: {"reveal_file_in_finder": "y", "reveal_file_in_finder_path": "..."}

item.run_script("/path/to/bin/my-workflow write-file-request --content 'hello'")
# variables: {"run_script": "y", "run_script_arg": "..."} + item.arg = cmd

item.terminal_command("echo hello")
# variables: {"terminal_command": "y", "terminal_command_arg": "..."} + item.arg = cmd

item.send_notification(title="Done", subtitle="File written")
# variables: {"send_notification": "y", "send_notification_title": "Done", "send_notification_subtitle": "..."}
```

**Alfred Conditional widget config** (one-time setup in Alfred UI):
```
if {var:open_url}          = y  →  Open URL widget        URL: {var:open_url_arg}
if {var:open_file}         = y  →  Open File widget       File: {var:open_file_path}
if {var:run_script}        = y  →  Run Script widget      Script: {query}
if {var:send_notification} = y  →  Post Notification      Title: {var:send_notification_title}
                                                          Subtitle: {var:send_notification_subtitle}
```

**Combining actions** — e.g. run_script + send_notification:
```python
item.run_script(cmd)
item.send_notification(title="Done", subtitle="success")
# Alfred: Run Script widget → connect forward to → Post Notification widget
```

**`sys.executable` trick** — Alfred's sandboxed shell has no `$PATH`, so always use absolute binary path:
```python
import sys
from pathlib import Path
bin_cli = Path(sys.executable).parent / "my-workflow"
cmd = f"{bin_cli} write-file-request --content {content!r}"
item.run_script(cmd)
# Works in both dev (.venv/bin/python) and production (uvx-managed python)
```

**Modifier key overrides** — hold ⌘ to show different subtitle/arg:
```python
import afwf.api as afwf
item.set_modifier(
    mod=afwf.ModEnum.cmd,       # "cmd" / "alt" / "ctrl" / "shift" / "cmd+alt" etc.
    subtitle="Press ⌘ to open folder instead",
    arg="/different/arg",
    valid=True,
)
# item.mods == {"cmd": {"subtitle": "...", "arg": "...", "valid": True}}
```

---

## QueryParser — Multi-Step Interactions

Alfred passes one raw query string. Use `Query` to branch on token count:

```python
import afwf.api as afwf

q = afwf.Query.from_str("username alice")
q.parts           # raw split result (includes empty strings from spaces)
q.trimmed_parts   # ["username", "alice"] — whitespace stripped, empties removed
q.n_trimmed_parts # 2

# Custom delimiter:
parser = afwf.QueryParser.from_delimiter("/")
q = parser.parse("2026/04/08")
q.trimmed_parts   # ["2026", "04", "08"]

# Multiple delimiters:
parser = afwf.QueryParser.from_delimiter([" ", ","])
```

**Standard two-step pattern** (pick key → enter value):
```python
@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    q = afwf.Query.from_str(query)

    if q.n_trimmed_parts == 0:
        return build_all_items()               # show everything

    elif q.n_trimmed_parts == 1:
        return fuzzy_filter(q.trimmed_parts[0])  # narrow by first token

    else:
        key   = q.trimmed_parts[0]
        value = " ".join(q.trimmed_parts[1:])
        return build_confirmation(key, value)  # confirmation item with run_script
```

---

## log_error Decorator

Alfred silently swallows Python exceptions — nothing shows in the UI. `log_error` writes tracebacks to a rotating log file on disk:

```python
import afwf.api as afwf

@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    ...
# Writes to: ~/.alfred-afwf/error.log

@afwf.log_error(log_file="~/.alfred-afwf/my_filter.log")
def main(query: str) -> afwf.ScriptFilter:
    ...

@afwf.log_error(log_file="~/.alfred-afwf/my_filter.log", tb_limit=5, max_bytes=200_000, backup_count=1)
def main(query: str) -> afwf.ScriptFilter:
    ...
```

Parameters: `log_file` (default `~/.alfred-afwf/error.log`), `tb_limit` (traceback depth), `max_bytes` (default 500 000), `backup_count` (default 2).

Log format: `[YYYY-MM-DD HH:MM:SS]` + traceback + 60-char separator. Transparent on happy path — zero overhead.

Uses `@functools.wraps`, so `main.__wrapped__` gives you the original undecorated function (important for testing — see below).

---

## Fuzzy Matching (`afwf[fuzzy]`)

Install: `uv add "afwf[fuzzy]"` or `pip install "afwf[fuzzy]"`

### opt.fuzzy_item — For Alfred Items (recommended)

```python
import afwf.api as afwf
import afwf.opt.fuzzy_item.api as fuzzy_item

# fuzzy_item.Item is a subclass of afwf.Item — use it the same way
item = fuzzy_item.Item(title="Alfred App", subtitle="https://alfredapp.com/")
item.set_fuzzy_match_name("Alfred App")
# Stores match name in item.variables["fuzzy_match_name"]
# item.fuzzy_match_name  → read-back property

items = [...]   # list of fuzzy_item.Item objects

matcher = fuzzy_item.FuzzyItemMatcher.from_items(items)
matched = matcher.match("alfred", threshold=70, limit=20)

# Always fall back to full list when no match (never show an empty pane):
return afwf.ScriptFilter(items=matched if matched else items)
```

### opt.fuzzy — Generic (for non-Item domain objects)

```python
from afwf.opt.fuzzy.api import FuzzyMatcher
import dataclasses

@dataclasses.dataclass
class Bookmark:
    title: str
    url: str

class BookmarkMatcher(FuzzyMatcher[Bookmark]):
    def get_name(self, item: Bookmark) -> str | None:
        return item.title   # return None to exclude item from match index

matcher = BookmarkMatcher.from_items(bookmarks)
# or: BookmarkMatcher.from_mapper({"name": [item1, item2]})

results = matcher.match("alfred", threshold=0)
```

**`match()` parameters:**
- `threshold=70` — minimum score 0–100; use `0` to return all sorted by score
- `limit=20` — max results
- `filter_func=lambda name, score, index: True` — extra filter applied after scoring

Items with the same `get_name()` value are all returned when that name matches.

---

## Typed Disk Cache (`afwf[cache]`)

Install: `uv add "afwf[cache]"` or `pip install "afwf[cache]"`

Alfred runs Script Filters on every keystroke. Cache expensive calls so Alfred stays responsive:

```python
import afwf.api as afwf
from afwf.opt.cache.api import TypedCache
from pathlib import Path

# Cache lives in ~/.alfred-afwf/.cache — created automatically on first use
# path_enum.dir_afwf resolves to Path.home() / ".alfred-afwf"
cache = TypedCache(Path.home() / ".alfred-afwf" / ".cache")

# Decorate the EXPENSIVE function — not main() itself
@cache.typed_memoize(expire=60)   # TTL in seconds; None = never expires
def fetch_data(query: str) -> list[str]:
    # slow: network call, disk scan, subprocess, etc.
    ...

@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    data = fetch_data(query)   # returns cached value after first call
    ...
```

`typed_memoize` parameters:
- `expire=None` — TTL in seconds; `None` = never expires
- `tag=None` — string tag for bulk eviction: `cache.evict(tag="my_tag")`
- `name=None` — override cache key prefix (default: function's qualified name)
- `typed=False` — when `True`, `f(1)` and `f(1.0)` cached separately
- `ignore=()` — argument names to exclude from the cache key

Preserves type hints (unlike plain `diskcache.memoize`).

Cache invalidation:
```python
cache.clear()               # delete everything
cache.evict(tag="my_tag")   # delete all entries with this tag
cache.delete(key)           # delete one key
```

**Note:** Each `uvx` call is a fresh process, but the cache persists on disk between Alfred invocations because it's stored in `~/.alfred-afwf/.cache`.

---

## Patterns

### Read-Only: Python-Side Fuzzy Filtering

Script is invoked on every keystroke; Python narrows the list.

```python
# my_pkg/search_items.py
import afwf.api as afwf
import afwf.opt.fuzzy_item.api as fuzzy_item

ITEMS_DATA = [
    {"title": "Python Docs", "url": "https://docs.python.org/"},
    {"title": "Alfred App",  "url": "https://alfredapp.com/"},
    # ...
]

@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    items = []
    for d in ITEMS_DATA:
        item = fuzzy_item.Item(title=d["title"], subtitle=d["url"])
        item.set_fuzzy_match_name(d["title"])
        item.open_url(d["url"])
        items.append(item)

    if query:
        matcher = fuzzy_item.FuzzyItemMatcher.from_items(items)
        matched = matcher.match(query, threshold=0)
        items = matched if matched else items   # never show empty pane

    return afwf.ScriptFilter(items=items)
```

Alfred plist: `argumenttype=1` (required), `alfredfiltersresults=false`

### Read-Only: Alfred-Side Filtering

Script runs once; Alfred filters the returned list as the user types (no re-invocation).

```python
# my_pkg/list_files.py
import afwf.api as afwf
from pathlib import Path

@afwf.log_error()
def main() -> afwf.ScriptFilter:
    sf = afwf.ScriptFilter()
    for p in sorted(Path("src/").glob("*.py")):
        item = afwf.Item(title=p.name, subtitle=f"Open {p.name}")
        item.match = p.name          # Alfred filters on this field
        item.autocomplete = p.name   # Tab fills this into search box
        item.open_file(path=str(p.resolve()))
        sf.items.append(item)
    return sf
```

Alfred plist: `argumenttype=2` (no argument), `alfredfiltersresults=true`

### Write Action: run_script + send_notification

Phase 1 (Script Filter, every keystroke): build the command string.
Phase 2 (user presses Enter): Alfred's Run Script widget executes the command.

```python
# my_pkg/write_file.py
import sys
import afwf.api as afwf
from pathlib import Path

path_file = Path.home() / ".alfred-afwf" / "file.txt"

def _build_cmd(content: str) -> str:
    bin_cli = Path(sys.executable).parent / "my-workflow"
    return f"{bin_cli} write-file-request --content {content!r}"

@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    item = afwf.Item(title=f"Write: {query}", subtitle=str(path_file))
    item.run_script(_build_cmd(query))
    item.send_notification(title="File written", subtitle=query)
    return afwf.ScriptFilter(items=[item])

def write_request(content: str) -> None:
    """Entry point for Alfred's Run Script widget — NOT a Script Filter."""
    path_file.parent.mkdir(parents=True, exist_ok=True)
    path_file.write_text(content)
```

Alfred workflow graph:
```
Script Filter → Conditional (run_script=y) → Run Script {query}
                                                  └→ Post Notification
                                                       Title: {var:send_notification_title}
                                                       Subtitle: {var:send_notification_subtitle}
```

### Conditional Display: Error State

```python
# my_pkg/read_file.py
import afwf.api as afwf
from pathlib import Path

path_file = Path.home() / ".alfred-afwf" / "file.txt"

@afwf.log_error()
def main() -> afwf.ScriptFilter:
    if not path_file.exists():
        item = afwf.Item(
            title=f"{path_file} does not exist",
            icon=afwf.Icon(path=afwf.IconFileEnum.error),
            valid=False,
        )
    else:
        content = path_file.read_text()
        item = afwf.Item(title=str(path_file), subtitle=content)
    return afwf.ScriptFilter(items=[item])
```

### Settings Store Pattern

Use a JSON-backed dict for persistent workflow settings:

```python
# my_pkg/settings.py
import json
from enum import Enum
from pathlib import Path

class SettingsKeyEnum(str, Enum):
    username = "username"
    theme    = "theme"

class _JsonSettings:
    def __init__(self, path: Path):
        self._path = path

    def __getitem__(self, key: str):
        if not self._path.exists():
            return None
        return json.loads(self._path.read_text()).get(key)

    def __setitem__(self, key: str, value: str):
        data = json.loads(self._path.read_text()) if self._path.exists() else {}
        data[key] = value
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data))

settings = _JsonSettings(Path.home() / ".alfred-afwf" / "settings.json")
```

---

## Testing

All tests use plain `pytest` — no Alfred needed.

### Pattern 1: Standalone file with coverage

```python
# tests/test_search_items.py
from my_pkg.search_items import main

class TestMain:
    def test_empty_query_returns_all(self):
        sf = main(query="")
        assert len(sf.items) > 0

    def test_query_filters(self):
        sf = main(query="python")
        assert any("Python" in item.title for item in sf.items)

    def test_no_match_returns_full_list(self):
        sf = main(query="zzz_no_match_zzz")
        assert len(sf.items) > 0   # never empty

if __name__ == "__main__":
    from afwf.tests import run_cov_test
    run_cov_test(__file__, "my_pkg.search_items", preview=False)
```

Run single file: `python tests/test_search_items.py` → pytest + coverage for that module only.
Run full suite: `mise run cov`

### Pattern 2: Monkeypatching module-level state

```python
import my_pkg.write_file as mod

def test_creates_file(self, tmp_path, monkeypatch):
    p = tmp_path / "file.txt"
    monkeypatch.setattr(mod, "path_file", p)   # patch on the module object
    mod.write_request("hello")
    assert p.read_text() == "hello"
```

For singletons imported at module load time, patch **both** modules:
```python
import my_pkg.settings as settings_mod
import my_pkg.set_settings as mod

patched = _JsonSettings(tmp_path / "settings.json")
monkeypatch.setattr(settings_mod, "settings", patched)
monkeypatch.setattr(mod, "settings", patched)   # also patch the re-import
```

For cache + memoized functions (decorator applied at import time, must re-apply):
```python
from afwf.opt.cache.api import TypedCache
import my_pkg.memoize_handler as mod

mod.cache = TypedCache(tmp_path / ".cache")
mod._get_value = mod.cache.typed_memoize(expire=5)(lambda key: 42)
```

### Pattern 3: Testing log_error via `__wrapped__`

`log_error` uses `@functools.wraps`, so `main.__wrapped__` is the original function. Re-decorate with a tmp log path:

```python
import afwf.api as afwf
import my_pkg.search_items as mod

def test_error_writes_log(self, tmp_path):
    log_file = tmp_path / "test.log"
    patched_main = afwf.log_error(log_file=log_file)(mod.main.__wrapped__)

    with pytest.raises(ValueError, match="simulated error"):
        patched_main(query="error")

    assert log_file.exists()
    content = log_file.read_text()
    assert "ValueError" in content
```

### Pattern 4: Assert on model, not serialized JSON

```python
# Good — readable, decoupled from serialization format
item = sf.items[0]
assert item.variables["run_script"] == "y"
assert "write-file-request" in item.arg
assert item.icon.path == str(afwf.IconFileEnum.error)

# Avoid — brittle
assert '"run_script": "y"' in json.dumps(sf.to_script_filter())
```

**Don't test:** Alfred widget routing, `to_script_filter()` format, `uvx` invocation.

---

## Deployment

### Dev (local venv)

Alfred Script field: `.venv/bin/my-workflow search-items --query '{query}'`

### Production (uvx)

```bash
~/.local/bin/uvx --from "my-pkg==1.0.1" my-workflow search-items --query '{query}'

# With optional extras:
~/.local/bin/uvx --from "my-pkg[fuzzy,cache]==1.0.1" my-workflow search-items --query '{query}'
```

`uvx` downloads, caches, runs — no virtualenv. Subsequent calls use cache; latency is negligible.

### Release checklist

1. Bump version in `_version.py` (and `pyproject.toml` if separate)
2. Run full test suite: `mise run cov`
3. `uv build && uv publish`
4. Update `script` field in Alfred's plist for each Script Filter node
5. Re-export `.alfredworkflow` bundle if distributing to users

### `info.plist` Script Filter node — key fields

```xml
<key>keyword</key>       <string>my-search</string>
<key>script</key>        <string>.venv/bin/my-workflow search-items --query '{query}'</string>
<key>argumenttype</key>  <integer>1</integer>   <!-- 0=optional, 1=required, 2=none -->
<key>alfredfiltersresults</key>  <false/>        <!-- false=Python filters, true=Alfred filters -->
<key>withspace</key>     <true/>
```

Keep `info.plist` in repo with **dev** paths. Production `uvx` paths live only in Alfred's installed copy.

---

## Quick Reference

```python
import afwf.api as afwf
import afwf.opt.fuzzy_item.api as fuzzy_item  # if using afwf[fuzzy]
from afwf.opt.cache.api import TypedCache      # if using afwf[cache]
from pathlib import Path

# Minimal Script Filter
@afwf.log_error()
def main(query: str) -> afwf.ScriptFilter:
    item = afwf.Item(title="Hello", subtitle=query)
    item.open_url("https://example.com")
    return afwf.ScriptFilter(items=[item])

# In cli.py:
# main(query=query).send_feedback()
```

| Need | Use |
|---|---|
| Return items to Alfred | `afwf.ScriptFilter(items=[...]).send_feedback()` |
| Open URL on Enter | `item.open_url(url)` |
| Open file on Enter | `item.open_file(path=str_path)` |
| Run shell command on Enter | `item.run_script(cmd)` + `sys.executable` trick |
| Notify on Enter | `item.send_notification(title, subtitle)` |
| Alt subtitle on ⌘+Enter | `item.set_modifier(afwf.ModEnum.cmd, subtitle=..., arg=...)` |
| Bundled error icon | `afwf.Icon(path=afwf.IconFileEnum.error)` |
| Parse query tokens | `afwf.Query.from_str(query).n_trimmed_parts` |
| Fuzzy filter items | `fuzzy_item.FuzzyItemMatcher.from_items(items).match(query)` |
| Cache slow calls | `@cache.typed_memoize(expire=60)` where `cache = TypedCache(Path.home() / ".alfred-afwf" / ".cache")` |
| Log errors to disk | `@afwf.log_error()` or `@afwf.log_error(log_file="~/.alfred-afwf/my.log")` |
| Disable item (Enter does nothing) | `item.valid = False` |
| Alfred filters results (client-side) | Set `item.match = "..."` and `alfredfiltersresults=true` in plist |
