# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是根据 key 随机生成一个 1 ~ 1000 之间的 value. 这个 value 的值
将会被缓存 5 秒. 5 秒内查询同一个 key 的结果将会是一样的. 该例子用来展示如何使用 time to live
缓存.

在 Alfred Workflow 的 Canvas 界面中 Script Filter 的设置如下:

- Keyword: afwf-example-memorize-cache, Argument Required
- Language: /bin/bash
- Script: python main.py 'memorize_cache {query}'
"""

import random
import afwf
import attr

from ..cache import cache


@attr.define
class Handler(afwf.Handler):
    @cache.memoize(tag="memorize_cache", expire=5)
    def main(self, key: str) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        value = random.randint(1, 1000)
        item = afwf.Item(
            title=f"value is {value}",
        )
        sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return dict(
            key=query,
        )


handler = Handler(id="memorize_cache")
