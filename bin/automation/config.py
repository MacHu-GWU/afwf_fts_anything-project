# -*- coding: utf-8 -*-

"""
Automation config management.
"""

import dataclasses
from pathlib_mate import Path


@dataclasses.dataclass
class AutomationConfig:
    python_version: str = dataclasses.field()
    dir_workflow: Path = dataclasses.field()


config = AutomationConfig(
    python_version="3.8",
    dir_workflow=Path(
        "/Users/sanhehu/Documents/Alfred-Preferences/Alfred.alfredpreferences/workflows/user.workflow.CE2F3D61-2353-4F28-ACC5-1FC134BEA746"
    ),
)
