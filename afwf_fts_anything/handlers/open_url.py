# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是展示一些预先定义好的网站的名字和 URL. 然后选中后按回车就会在浏览器
内打开对应网站.

这个 Script Filter 没有输入参数. 所以 ``main()`` 函数也没有参数. 那么我们在实现
``parse_query()`` 函数的时候直接返回空字典即可.

在 Alfred Workflow 的 Canvas 界面中 Script Filter 的设置如下:

- Keyword: afwf-example-open-url, No Argument
- Language: /bin/bash
- Script: python main.py 'open_url {query}', 这里我们没有勾选 Alfred filters results. 因为我们不需要 Alfred 帮我们过滤结果.
- 连接一个 Utilities - Conditional 的控件, 条件是 ``{var:open_url}`` is equal to ``y``.
- 连接一个 Actions - Open Url 的控件, URL 的参数是 ``{var:open_url_arg}``.
"""

import afwf
import attr


@attr.define
class Handler(afwf.Handler):
    def main(self) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        for title, url in [
            ("Alfred App", "https://www.alfredapp.com/"),
            ("Python", "https://www.python.org/"),
            ("GitHub", "https://github.com/"),
        ]:
            item = afwf.Item(
                title=title,
                subtitle=f"open {url}",
                autocomplete=title,
                arg=url,
            )
            item.open_url(url=url)
            sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return {}


handler = Handler(id="open_url")
