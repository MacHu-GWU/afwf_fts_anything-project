# -*- coding: utf-8 -*-

import afwf

from .handlers import (
    fts,
)

wf = afwf.Workflow()
wf.register(fts.handler)
