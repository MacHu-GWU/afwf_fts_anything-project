# -*- coding: utf-8 -*-

import afwf
import attr
from afwf.workflow import log_debug_info


@attr.define
class Handler(afwf.Handler):
    def main(self) -> afwf.ScriptFilter:
        log_debug_info("before raising the error")
        raise Exception("raise this error intentionally")

    def parse_query(self, query: str):
        return {}


handler = Handler(id="error")
