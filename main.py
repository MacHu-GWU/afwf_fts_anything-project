# -*- coding: utf-8 -*-

"""
[CN]
Alfred Workflow Script Filter 的入口主文件, 适用于所有的 Python Alfred Workflow 项目.
如果你不懂这个文件起什么作用, 最多你可以修改 ``debug=True``, 请不要修改其他部分.

How it works:

这个文件只应该在 Alfred Workflow 真正的目录下被运行, 而不应该是在这个 Git repo 的开发目录
下被运行. 真正的目录路径长这个样子
``/path/to/Alfred.alfredpreferences/workflows/user.workflow.ABCD1234-A1B2-C3D4-E5F6-A1B2C3D4E5F6``.

这个文件的核心逻辑是, 根据文件本身的位置定位到 ``lib`` 目录所在的位置, 并将其加入到 ``sys.path`` 中,
这样 Python 依赖就可以被找到了. 然后再从你的 workflow 源码包中导入 Workflow 对象, 并运行它.
"""

import sys
from pathlib import Path

dir_here = Path(__file__).absolute().parent
dir_lib = Path(dir_here, "lib")

if dir_lib.exists():
    sys.path = [str(dir_lib), ] + sys.path

if __name__ == "__main__":
    from afwf_fts_anything import wf

    wf.run(debug=True)
