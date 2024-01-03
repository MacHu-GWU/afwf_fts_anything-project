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
        "/Users/sanhehu/Documents/Alfred-Setting/Alfred.alfredpreferences/workflows/user.workflow.029AD850-D41F-4B53-B495-35061A408298",
    ),
)
