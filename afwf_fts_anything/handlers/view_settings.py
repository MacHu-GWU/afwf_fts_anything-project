# -*- coding: utf-8 -*-

import afwf
import attr

from ..settings import settings, SettingsKeyEnum


@attr.define
class Handler(afwf.Handler):
    def main(self) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        for settings_key in SettingsKeyEnum:
            value = settings.get(settings_key.value)
            item = afwf.Item(
                title=f"settings.{settings_key} = {value!r}",
            )
            sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return {}


handler = Handler(id="view_settings")
