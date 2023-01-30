# -*- coding: utf-8 -*-

"""
[CN]
Alfred Workflow Script Filter 的入口主文件, 适用于所有的 Python Alfred Workflow 项目.
如果你不懂这个文件起什么作用, 最多你可以修改 ``debug=True``, 请不要修改其他部分.
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
