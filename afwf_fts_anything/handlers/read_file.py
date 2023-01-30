# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是展示 file.txt 文件中的内容. 仅仅是和 ``write_file.py`` 模块
配合使用, 永远验证.
"""

import sys
import afwf
import attr

from ..paths import dir_project_home


@attr.define
class Handler(afwf.Handler):
    def main(self) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        path = dir_project_home / "file.txt"
        if path.exists():
            content = path.read_text()
            item = afwf.Item(
                title=f"content of file.txt is",
                subtitle=content,
            )
        else:
            item = afwf.Item(
                title="file.txt does not exist!",
            )
            item.set_icon(afwf.IconFileEnum.error)

        sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return {}


handler = Handler(id="read_file")
