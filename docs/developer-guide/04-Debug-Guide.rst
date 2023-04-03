Debug Guide
==============================================================================


Summary
------------------------------------------------------------------------------
在前一章节 Development Guide 中我们已经介绍了如何用单元测试来确保代码的正确性. 但是有一些功能是在你真正使用 Alfred Workflow 的时候才会遇到的. 而 Alfred Workflow 自带的 debug 工具过于简陋, 出错了也不会给我们任何视觉上的提示. 我们希望能在出错的时候显示我们平时运行 Python 程序时的 Traceback 信息. 下面我们来介绍这一问题的解决方案.


The Solution
------------------------------------------------------------------------------
afwf 框架中的 `Workflow <https://github.com/MacHu-GWU/afwf-project/blob/main/afwf/workflow.py>`_ 模块对主逻辑有封装. 这里有两种 debug 机制可以帮助我们排查问题:

1. 当主逻辑有错误时 (即 raise 了一个 Exception), 那么在 Python 的 traceback 日志则会被保存到 ``${HOME}/.alfred-afwf/last-error.txt`` 文件中, 每次出现错误都会覆盖这个文件.
2. 你的 `main.py <https://github.com/MacHu-GWU/afwf-project/blob/main/main.py>`_ 文件中 ``wf.run(debug=True)`` 如果设置了 ``debug=True``, 那么你可以用 ``afwf.log_debug_info("message")`` 函数来记录一些调试信息. 这些 debug 日志会以 append only 的形式保存到 ``${HOME}/.alfred-afwf/debug.txt`` 中.

默认 afwf 框架会在出错时返回两个 Item, 一个可以一键打开 ``last-error.txt`` 文件, 一个可以一键打开 ``debug.txt`` 文件. 但是前提你要给你的每个 Script Filter 的后继 Action 连接一个 ``Utilities -> Conditional`` 的控件, 其中 if 的判断值设为 ``{var:_open_log_file}`` (注意下划线), 条件设置为 is equal to "y". 然后连接一个 ``Actions -> Open File`` 的控件, 其中 File 设为 ``{var:_open_log_file_path}`` (注意下划线). 这样就能使得的自动出现的两个用于 debug 的 items 能一键打开日志文件了.


Next
------------------------------------------------------------------------------
`Unit Test Guide <./05-Unit-Test-Guide.rst>`_