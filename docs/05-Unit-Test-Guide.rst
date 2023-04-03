Unit Test Guide
==============================================================================


Overview
------------------------------------------------------------------------------
对 Alfred Workflow 的源码进行单元测试一直是一个大难题. 这里我们利用了 `afwf <https://github.com/MacHu-GWU/afwf-project>`_ 框架中的 ``Handler`` 类. 每一个 ``Handler`` 类都有两个方法, ``def main(...)`` 和 ``def handler(...)``. 其中 ``main`` 实现了核心的业务逻辑, 其本质就是一个 Python 函数, 你就按照正常的方式进行输入输出的单元测试即可. 而 ``handler`` 只是对 ``main`` 的一层封装, 将 input box 中的 query str 解析成 arg 传给 ``main`` 方法而已. 因此我们可以将 parse query 的逻辑单独做单元测试. 这样单元测试就已经完成了 99% 的工作了. 剩下的 1% 就是对 Workflow 的 Integration Test 了.


Example
------------------------------------------------------------------------------
这里我们拿 `memorize_cache.py <../afwf_fts_anything/handlers/memorize_cache.py>`_ 为例. 它的核心逻辑是根据 Key 生成一个随机数, 并且缓存 5 秒. 返回的对象是一个 ``ScriptFilter`` 对象, 而这个生成的随机数则保存在 ``ScriptFilter.items`` 列表中.

我们再来看 `test_handler_memorize_cache.py <../tests/test_handler_memorize_cache.py>`_ 的测试用例. 测试用例仅仅是用同一个 key 调用了两次 ``main`` 函数, 然后比较 item 的 title 是不是一样. 是一样说明缓存起作用了.


Next
------------------------------------------------------------------------------
`Release Guide <./06-Release-Guide.rst>`_
