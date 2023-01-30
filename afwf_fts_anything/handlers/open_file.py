# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是展示当前这个 handlers 文件夹下的所有 Python 文件供用户选择,
用户可以用上下选择文件, 也可以输入字符来过滤文件. 选中后按回车就会用默认应用打开对应的文件.

我们准备用 Alfred filters results 功能帮我们过滤文件, 所以我们无需在 main() 中接收参数,
 免去了自己实现过滤文件的功能. 那么我们在实现 ``parse_query()`` 函数的时候直接返回空字典即可.

在 Alfred Workflow 的 Canvas 界面中 Script Filter 的设置如下:

- Keyword: afwf-example-open-file, Argument Optional
- Language: /bin/bash
- Script: python main.py 'open_file {query}'
- Alfred filters results: checked
- 连接一个 Utilities - Conditional 的控件, 条件是 ``{var:open_file}`` is equal to ``y``.
- 连接一个 Actions - Open File 的控件, File 的参数是 ``{var:open_file_path}``.
"""

import afwf
import attr
from pathlib_mate import Path


@attr.define
class Handler(afwf.Handler):
    def main(self) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        dir_here = Path.dir_here(__file__)
        for p in dir_here.iterdir():
            if p.ext.lower() == ".py":
                item = afwf.Item(
                    title=p.basename,
                    subtitle=f"Open {p.abspath}",
                    autocomplete=p.basename,
                    match=p.basename,
                    arg=p.abspath,
                )
                item.open_file(path=p.abspath)
                sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return {}


handler = Handler(id="open_file")
