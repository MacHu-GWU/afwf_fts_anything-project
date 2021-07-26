# -*- coding: utf-8 -*-

import workflow
from afwf_fts_anything.handlers import handler

wf = workflow.Workflow3()
handler(wf, args=["cloudformation", "res", "ec2", "inst"])
