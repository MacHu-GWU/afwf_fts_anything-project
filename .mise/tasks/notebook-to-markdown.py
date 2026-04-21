# -*- coding: utf-8 -*-

"""
Convert Jupyter notebooks in docs/source/ to Markdown files.
"""

import subprocess
from pathlib import Path

# Project root is two levels up from this script
project_root = Path(__file__).parent.parent.parent
dir_sphinx_doc_source = project_root / "docs" / "source"
path_jupyter = project_root / ".venv" / "bin" / "jupyter"

for path_notebook in dir_sphinx_doc_source.glob("**/*.ipynb"):
    if ".ipynb_checkpoints" in str(path_notebook):
        continue
    path_markdown = path_notebook.parent / "index.md"
    args = [
        str(path_jupyter),
        "nbconvert",
        "--to",
        "markdown",
        str(path_notebook),
        "--output",
        str(path_markdown),
    ]
    print(f"Converting: {path_notebook.relative_to(project_root)}")
    subprocess.run(args, check=True)
