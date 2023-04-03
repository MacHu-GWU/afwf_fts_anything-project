Release Guide
==============================================================================


Summary
------------------------------------------------------------------------------
我们希望能将开发好的 Workflow 发布出去供大家下载. 并且希望安装的过程尽可能的简单. 作为 Workflow 的开发者, 我们希望简化发布新版本的流程.


Solution
------------------------------------------------------------------------------
1. 首先运行一次 ``make cov`` 命令执行代码覆盖率单元测试, 确保 90% 以上的覆盖率. 不然你自己都说服不了自己你的 Workflow 会不会有严重的 Bug.
2. 然后运行一次 ``make build-wf`` 命令从源代码构建 Alfred Workflow. 保证你即将发布的 Workflow 的代码跟你的代码库中一致.
3. 在 Alfred 中输入 ``?Workflow`` 进入 Alfred Workflow 菜单.
4. 找到你的 Workflow, 点击右键呼出菜单, 然后点击 ``Export`` 进入导出页面.
5. 给你的 Workflow 加上一些 Metadata. 例如:
    - Bundle Id: 可以是 ``${GitHubUserName}-${ProjectName}`` 的格式
    - Version: 用 Semantic Version 的方式命名. 从 ``0.1.1`` 开始
6. 导出后将文件重命名为这种格式: ``${ProjectName}-${SemanticVersion}-${OS}_${PlatForm}.alfredworkflow``, 例如: ``afwf_fts_anything-0.1.1-macosx_arm64.alfredworkflow``.
7. 在 GitHub Repo 中的 Release 菜单里点击 ``Draft a new release``. 然后设置 Tag 为你的 Semantic Version, Release Title 也是一样. 然后在将你刚才创建的 ``.alfredworkflow`` 文件拖曳到 ``Attach binaries by dropping them here or selecting them.`` 区域上传.
8. 至此你的用户可以在 Release 中点击 ``.alfredworkflow`` 文件下载然后双击安装你的 Workflow 了.

**全文完**
