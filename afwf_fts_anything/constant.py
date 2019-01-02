# -*- coding: utf-8 -*-

"""
dir settings
"""

from __future__ import unicode_literals
from pathlib_mate import PathCls as Path

HOME = Path.home()
"""
User home directory:

- Windows: C:\\Users\\<username>
- MacOS: /Users/<username>
- Ubuntu: /home/<username> 
"""

ALFRED_FTS = Path(HOME, ".alfred-fts")
"""
Alfred Full Text Search Data Folder: ${HOME}/.alfred-fts
"""

if not ALFRED_FTS.exists():
    ALFRED_FTS.mkdir()
