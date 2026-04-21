---
name: py-changelog
description: Maintain the release-history.rst changelog for a Python project before publishing a new version. Use when the user wants to prepare release notes, update changelog, or is about to publish/tag a new version.
---

You are maintaining `release-history.rst` for a Python project. Your job is to keep the target version's section accurate and complete based on git history. You never touch the `x.y.z (Backlog)` section.

## Step 1: Gather State

Run these commands to understand the current state:

```bash
# Last published tag
git describe --tags --abbrev=0

# pyproject.toml version (this is the target version to release)
grep '^version' pyproject.toml
```

**Determine target version:**
- `pyproject.toml version` is always the source of truth for the new release target.
- `last tag` is the baseline for git history comparison.

## Step 2: Pull Git Changes (Feed to AI)

Use `{LAST_TAG}` = the tag from Step 1.

```bash
# Commit intent summary
git log {LAST_TAG}..HEAD --oneline

# Files changed (concise overview)
git diff {LAST_TAG}..HEAD --stat

# Actual Python code changes (for understanding what really changed)
git diff {LAST_TAG}..HEAD -- '*.py'
```

Read these outputs carefully. They are the ground truth for what changed.

## Step 3: Read release-history.rst Format

Read the first 100 lines of `release-history.rst`:

```bash
head -100 release-history.rst
```

This shows you:
- The RST formatting conventions used in this project
- The section categories (Features and Improvements, Minor Improvements, Bugfixes, Breaking Changes, Miscellaneous)
- The `x.y.z (Backlog)` placeholder at the top — **never modify this section**
- The Backlog content — use it as **reference only** to understand what the user plans, do not copy or move it

## Step 4: Determine Action

**Case A — Target version section already exists in release-history.rst:**

Compare the existing content against what git history reveals:
- Is anything missing that git history shows?
- Is anything written that git history does not support?
- Are the descriptions accurate and clear?

Update the section in-place to be complete and accurate. Do not leave gaps.

**Case B — Target version section does not exist:**

Insert a new section immediately after the `x.y.z (Backlog)` block (after its blank line), following this exact RST format:

```rst
{VERSION} ({DATE})
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- ...

**Minor Improvements**

- ...

**Bugfixes**

- ...

**Miscellaneous**

- ...
```

Use today's date. Omit any category that has no entries (do not leave empty `**Category**` headers with no bullets).

## Step 5: Write Directly

Edit `release-history.rst` directly. No need to ask the user for confirmation — the file is git-tracked and can be reverted.

## Rules

- **Never touch `x.y.z (Backlog)`** — not its header, not its content, not its blank lines.
- Backlog content is reference only. Do not copy bullet points verbatim from Backlog into the version section.
- Base all changelog entries on what git history actually shows, not assumptions.
- Keep descriptions user-facing and concise (what changed and why it matters, not implementation details).
- Follow the RST formatting exactly as seen in existing entries.
- If a category has no entries, omit the entire category header.
