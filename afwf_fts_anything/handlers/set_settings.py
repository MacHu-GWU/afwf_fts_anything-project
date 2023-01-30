# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是让用户对用作 settings 的 sqlite 进行读写.
"""

import typing as T
import sys

import afwf
import attr

from ..settings import settings, SettingsKeyEnum
from ..fuzzymatch import ItemFuzzyMatcher


@attr.define
class SetSettingValueHandler(afwf.Handler):
    def main(self, key: str, value: str) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        settings[key] = value
        print(f"key = {key}, value = {value}")
        return sf

    def parse_query(self, query: str):
        key, value = query.split(" ", 1)
        return dict(
            key=key,
            value=value,
        )

    def encode_query(self, key: str, value: str) -> str:
        return f"{key} {value}"


set_setting_value_handler = SetSettingValueHandler(id="set_setting_value")


@attr.define
class Handler(afwf.Handler):
    def main(
        self,
        key: T.Optional[str] = None,
        value: T.Optional[str] = None,
    ) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()

        if key is None:
            for settings_key in SettingsKeyEnum:
                item = afwf.Item(
                    title=settings_key.value,
                    subtitle=f"set {settings_key.value} to ...",
                    autocomplete=settings_key.value + " ",
                )
                sf.items.append(item)
        elif value is None:
            items = list()
            for settings_key in SettingsKeyEnum:
                item = afwf.Item(
                    title=settings_key.value,
                    subtitle=f"set {settings_key.value} to ...",
                    autocomplete=settings_key.value + " ",
                )
                items.append(item)
            matcher = ItemFuzzyMatcher(mapper={item.title: item for item in items})
            sf.items.extend(matcher.match(query=key))
        else:
            if key in SettingsKeyEnum.__members__:
                item = afwf.Item(
                    title=f"Set settings.{key} = {value!r}",
                )
                item.send_notification(
                    title=f"Set settings.{key} = {value!r}",
                )
                cmd = set_setting_value_handler.encode_run_script_command(
                    bin_python=sys.executable,
                    key=key,
                    value=value,
                )
                item.run_script(cmd)
                sf.items.append(item)
            else:
                item = afwf.Item(
                    title=f"{key!r} is not a valid settings key",
                )
                item.set_icon(afwf.IconFileEnum.error)
                sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        parts = [part.strip() for part in query.split(" ", 1) if part.strip()]
        if len(parts) == 0:
            return dict(key=None, value=None)
        elif len(parts) == 1:
            return dict(key=parts[0], value=None)
        elif len(parts) == 2:
            return dict(key=parts[0], value=parts[1])
        else:
            raise NotImplementedError


handler = Handler(id="set_settings")
