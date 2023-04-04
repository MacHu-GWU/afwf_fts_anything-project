Development Guide
==============================================================================


Automation Scripts
------------------------------------------------------------------------------
跟自动化脚本有关的文件有这些:

- ``bin/``: 这个目录下存放的都是可执行的自动化脚本文件. 本质上都是用 Python 写的 shell script.
- ``bin/automation``: 这是一个 Python 库, 按照模块化存放了一些自动化脚本的函数.
- ``bin/s123_123_..._.py``: 一堆按照编号排序的自动化脚本, 都是开发工作流会用到的.
- ``Makefile``: 项目的自动化脚本入口, 本质上是对 ``bin/s123_123_..._.py`` 的封装.

在项目根目录下打 ``make`` 命令就能弹出一堆命令:

.. code-block:: make

    help                                     ** Show this help message
    venv-create                              ** Create Virtual Environment
    venv-remove                              ** Remove Virtual Environment
    install                                  ** Install main dependencies and Package itself
    install-dev                              Install Development Dependencies
    install-test                             Install Test Dependencies
    install-doc                              Install Document Dependencies
    install-all                              Install All Dependencies
    poetry-export                            Export requirements-*.txt from poetry.lock file
    poetry-lock                              Resolve dependencies using poetry, update poetry.lock file
    test                                     ** Run test
    test-only                                Run test without checking test dependencies
    cov                                      ** Run code coverage test
    cov-only                                 Run code coverage test without checking test dependencies
    build-wf                                 ** Build Alfred Workflow release from source code
    refresh-code                             ** Refresh Alfred Workflow source code

这里最常用到的几个是::

    venv-create
    install-all
    poetry-lock
    cov
    build-wf
    refresh-code


Automation Config
------------------------------------------------------------------------------
在 ``bin/automation/config.py`` 文件中, 有一个配置对象 ``AutomationConfig``, 它记录了自动化脚本所需要的一些配置. 其中 ``dir_workflow`` 最为重要, 它定义了 Alfred Workflow 实际保存的位置. 这个位置你可以在 Alfred 中创建一个 Workflow, 然后右键点击, 选择 Open in Finder 就能找到了. 路径大该长这个样子 ``/path/to/Alfred.alfredpreferences/workflows/user.workflow.ABCD1234-A1B2-C3D4-E5F6-A1B2C3D4E5F6``. 这个路径会被构建的自动化脚本所使用, 将你的源代码拷贝到对应的位置, 以实现 "安装" 的效果.


The Workflow Entry Point - main.py
------------------------------------------------------------------------------
在项目的根目录下有一个 `main.py <../main.py>`_ 文件. 这个文件是 Alfred Workflow 的入口脚本. , 也是 Alfred Workflow 的主要逻辑. 请跳转到文件的内容查看注释了解它的功能.


The Workflow Source Code
------------------------------------------------------------------------------
在项目的根目录下有一个 `afwf_fts_anything <../afwf_fts_anything>`_ 目录. 这个目录就是你的 Alfred Workflow 的源码了. 其中 `workflow.py <../afwf_fts_anything/workflow.py>`_ 模块定义了 Workflow 的对象实例. 并且将所有需要用到的 ``Handler`` 都注册了. 而 `handlers <../afwf_fts_anything/handlers>`_ 子模块则包含了所有的 handlers 的实现. 我建议查看所有示例 handlers 的源码来了解如何编写常见的 handler 逻辑.

- `error.py <../afwf_fts_anything/handlers/error.py>`_: 故意抛出异常, 用于测试异常处理逻辑.
- `memorize_cache.py <../afwf_fts_anything/handlers/memorize_cache.py>`_: 一个带磁盘缓存的记忆函数.
- `open_file.py <../afwf_fts_anything/handlers/open_file.py>`_: 可以用来选择并打开文件.
- `open_url.py <../afwf_fts_anything/handlers/open_url.py>`_: 可以用来选择并在浏览器中打开网页.
- `read_file.py <../afwf_fts_anything/handlers/read_file.py>`_: 对文件的内容进行读取.
- `write_file.py <../afwf_fts_anything/handlers/write_file.py>`_: 对文件的内容进行写入.
- `set_settings.py <../afwf_fts_anything/handlers/set_settings.py>`_: 对数据库进行写入.
- `view_settings.py <../afwf_fts_anything/handlers/view_settings.py>`_: 对数据库进行读取.


Next
------------------------------------------------------------------------------
`Debug Guide <./04-Debug-Guide.rst>`_
