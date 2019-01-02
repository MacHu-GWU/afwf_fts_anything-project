# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
from workflow import Workflow


def main(wf):
    """
    .. note::

        注意, 所有的第三方库的导入都要放在 main 函数内, 因为直到创建 Workflow 实例时,
        lib 目录才会被添加到系统路径中去. 在这之前所有的第三方库都无法被找到.
    """
    from afwf_fts_anything.handlers import main

    wf = main(wf)
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow(libraries=["lib", ])
    logger = wf.logger
    sys.exit(wf.run(main))
