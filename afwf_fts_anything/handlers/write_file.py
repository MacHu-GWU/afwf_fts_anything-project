# -*- coding: utf-8 -*-

"""
[CN]

该 Script Filter 的功能是让用户将文本写入特定文件. 该例子用来展示如何实现按下回车后执行任意
Python 逻辑. 该技巧可以用来实现按下回车后做到任何事情, 因为底层就是一个 Python 脚本.

其原理如下:

我们这里多了一个 ``WriteRequestHandler`` 的 handler. 这个 handler 并不会跟任何
Script Filter 所对应, 而是仅仅作为一个 CLI 命令行接口而存在. 这样我们在其他的 handler 中
只要将 item 之后的 action 定义为 Run Script, 那么就可以按下回车后用 bash 来执行任何
Python 逻辑. 而这个 bash command 就是 item 的 argument. 这个 ``WriteRequestHandler``
则是实现了 bash command 所对应的功能.

``WriteRequestHandler`` 实现了将任意 content 写入 file.txt 的功能. 并且在
``encode_query()`` 中实现了如何将 main 中的参数编码成字符串的函数.

``Handler`` 则实现了 Script Filter 的功能.

在 Alfred Workflow 的 Canvas 界面中 Script Filter 的设置如下:

- Keyword: afwf-example-write-file, Argument Required
- Language: /bin/bash
- Script: python main.py 'write_file {query}'
- 连接一个 Utilities - Conditional 的控件, 条件是 ``{var:run_script}`` is equal to ``y``.
- 连接一个 Actions - Run Script 的控件, Script 的参数是 ``{query}``.
- 连接一个 Utilities - Conditional 的控件, 条件是 ``{var:send_notification}`` is equal to ``y``.
- 连接一个 Outputs - Post Notification 的控件, Title 的参数是 ``{var:send_notification_title}``
    Subtitle 的参数是 ``{var:send_notification_subtitle}``.
"""

import sys
import afwf
import attr

from ..paths import dir_project_home


@attr.define
class WriteRequestHandler(afwf.Handler):
    def main(self, content: str) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        path = dir_project_home / "file.txt"
        path.write_text(content)
        return sf

    def parse_query(self, query: str):
        return dict(
            content=query,
        )

    def encode_query(self, content: str) -> str:
        return content


write_request_handler = WriteRequestHandler(id="write_request_handler")


@attr.define
class Handler(afwf.Handler):
    def main(self, content: str) -> afwf.ScriptFilter:
        sf = afwf.ScriptFilter()
        path = dir_project_home / "file.txt"
        item = afwf.Item(
            title=f"Write {content!r} to {path.basename}",
        )
        cmd = write_request_handler.encode_run_script_command(
            bin_python=sys.executable,
            content=content,
        )
        item.run_script(cmd)
        item.send_notification(
            title=f"Write {content!r} to {path.basename}",
            subtitle="success",
        )
        sf.items.append(item)
        return sf

    def parse_query(self, query: str):
        return dict(
            content=query,
        )


handler = Handler(id="write_file")
