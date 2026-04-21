Project Overview
==============================================================================

Overview
------------------------------------------------------------------------------
This project is an **AI-First Python open source skeleton** — a carefully crafted starting point that wires together the most advanced, battle-tested development toolchain available in 2026. From dependency management to CI/CD to coding agents, every component is chosen for speed, reliability, and developer happiness. If you're starting a new Python library, this is your launchpad.


Dev Tool Manager — mise
------------------------------------------------------------------------------
We use `mise (mise en place) <https://mise.jdx.dev>`_ to manage every developer tool in the project. The single source of truth is `mise.toml <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/mise.toml>`_. Throughout this guide, whenever a new tool is introduced, we'll always point back to the corresponding entry in that file.

Why mise? Because managing tools across a dozen repos is painful — and mise solves it elegantly:

- **Install once, reuse everywhere.** If ten repos all need Python 3.12, ``uv``, or ``claude``, mise installs each version exactly once and shares it. No redundant installs, no disk bloat, no global environment pollution.
- **Replace ``make`` with mise tasks.** Complex multi-step workflows (install, test, publish, release) become simple one-liners. No more cryptic Makefiles.
- **First-class environment variable management.** Per-project ``.env`` support with automatic activation — no more forgetting to ``source`` things.

The most important commands you'll use day-to-day:

- ``mise run inst`` — install all project dependencies
- ``mise run cov`` — run unit tests with coverage report
- ``mise run publish`` — publish the package to PyPI
- ``mise run release`` — cut a new release (tag, changelog, publish)


Package Manager — uv
------------------------------------------------------------------------------
We use `uv <https://docs.astral.sh/uv/>`_ as the Python package manager. It is hands-down the fastest resolver and installer in the Python ecosystem — written in Rust, with dependency resolution that outpaces pip and poetry by orders of magnitude.

All package metadata and dependencies live in `pyproject.toml <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/pyproject.toml>`_. You never need to call ``uv`` directly — ``mise run inst`` handles it for you.

- Lightning-fast installs (10–100x faster than pip in cold-cache scenarios)
- Deterministic lockfile for reproducible environments
- Seamlessly integrated with ``mise`` — zero friction


Coding Agent — Claude Code
------------------------------------------------------------------------------
We treat Claude Code as a first-class member of the development workflow. The project ships with a `CLAUDE.md <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/CLAUDE.md>`_ file that tells Claude exactly how the project is structured — which tools are in use, how to run tasks, where tests live, and how to navigate the codebase.

This means Claude can:

- Run ``mise run cov`` to execute tests and understand failures
- Navigate ``pyproject.toml`` for dependency context
- Follow the project's testing conventions without being told every time

No more copy-pasting boilerplate into every chat. The ``.claude/`` directory holds additional context files that keep the agent grounded in this project's specific conventions.


Unit Testing — pytest + Codecov
------------------------------------------------------------------------------
Tests are written with `pytest <https://docs.pytest.org>`_ and tracked via `codecov.io <https://codecov.io>`_. The relevant config files are:

- `codecov.yml <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/codecov.yml>`_ — Codecov reporting configuration
- `.coveragerc <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/.coveragerc>`_ — coverage measurement settings

A unique pattern used in this project: every test file can be run as a standalone script. The ``if __name__ == "__main__":`` block at the bottom of each test file invokes pytest as a subprocess, so you can iterate on a single test file in isolation without spinning up the full suite. Fast feedback, zero ceremony.

Run all tests with coverage in one shot:

.. code-block:: bash

    mise run cov


Documentation — Sphinx + Read the Docs
------------------------------------------------------------------------------
Documentation is built with `Sphinx <https://www.sphinx-doc.org>`_ from source files in `docs/source/ <https://github.com/MacHu-GWU/afwf_fts_anything-project/tree/main/docs/source>`_ and hosted automatically on `Read the Docs <https://readthedocs.org>`_.

The hosting config lives in `.readthedocs.yml <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/.readthedocs.yml>`_ — push to ``main`` and your docs update automatically. No manual deploys needed.

Build docs locally with:

.. code-block:: bash

    mise run build-doc


CI/CD — GitHub Actions
------------------------------------------------------------------------------
Continuous integration runs on GitHub Actions, configured in `.github/workflows/main.yml <https://github.com/MacHu-GWU/afwf_fts_anything-project/blob/main/.github/workflows/main.yml>`_.

The pipeline runs a **matrix build** across multiple Python versions and operating systems — the gold standard for open source library compatibility testing. Every pull request and push to ``main`` triggers:

- Dependency installation via ``uv``
- Full test suite with coverage upload to Codecov
- Documentation build validation


From Zero to Published in 60 Seconds
------------------------------------------------------------------------------
Here's the best part: you don't need to manually configure GitHub, Codecov, or Read the Docs separately. Our ``mise`` tasks handle the entire setup in one shot.

From the moment you pick a project name to the moment your package is live on PyPI — with full CI, coverage reporting, and hosted documentation — the whole journey takes about **one minute**.

That's the promise of this skeleton: stop configuring infrastructure, start shipping code.
