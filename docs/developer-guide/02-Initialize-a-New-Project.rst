Initialize a New Project
==============================================================================
当你决定开始用 Python 开发一个属于你自己的 Alfred Workflow 的时候, 你可以参考本文来生成你的 Git 项目文件. 大大减少了你手动设置的工作量.


Solution
------------------------------------------------------------------------------
**第一步, 创建一个新的 Git Repo**

1. 到这个开源 GitHub repo https://github.com/MacHu-GWU/cookiecutter-afwf, 这个 repo 是一个 Python Alfred Workflow 的模板. 将其 Clone 下来.
2. 进入这个配置文件 https://github.com/MacHu-GWU/cookiecutter-afwf/blob/main/cookiecutter-afwf.json, 填入你的项目相关的信息.
3. 给你的 Python 安装必要的依赖, 具体的值列在这里 https://github.com/MacHu-GWU/cookiecutter-afwf/blob/main/requirements.txt. 安装的命令是 ``pip install -r requirements.txt``.
4. 运行 https://github.com/MacHu-GWU/cookiecutter-afwf/blob/main/create_repo.py 脚本, 它会在 ``cookiecutter-afwf/tmp/`` 目录下生成你的项目文件夹. 运行的命令是 ``python create_repo.py``.

**第二步, 对你的项目进行一些配置**

1. 到 ``pyproject.toml`` 中的 ``[tool.poetry.dependencies]`` 一栏中填入你的项目所需的依赖.
2. 没有了.


Next
------------------------------------------------------------------------------
`Development Guide <./03-Development-Guide.rst>`_
