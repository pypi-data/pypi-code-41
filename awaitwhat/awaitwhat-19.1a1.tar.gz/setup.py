# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['awaitwhat']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'awaitwhat',
    'version': '19.1a1',
    'description': 'FIXME',
    'long_description': '# Await, What?\n\nTell you what waits for what in an `async/await` program.\n\n#### TL;DR\n\nSay you have this code:\n```py\n\nasync def job():\n    await foo()\n\n\nasync def foo():\n    await bar()\n\n\nasync def bar():\n    await baz()\n\n\nasync def baz():\n    await leaf()\n\n\nasync def leaf():\n    await asyncio.sleep(1)  # imagine you don\'t know this\n\n\nasync def work():\n    await asyncio.gather(..., job())\n```\n\nNow that code is stuck and and you want to know why.\n\nPython built-in tools give you this, and it\'s not helpful:\n```py\n---- task\n<frame at 0x7ffd90266378, file \'test/test.py\', line 46, code job>\n\n---- task\n<frame at 0x7ffd90080808, file \'test/test.py\', line 50, code work>\n```\n\nThis library gives you more:\n```py\n---- task\n<frame at 0x7ffd90266378, file \'test/test.py\', line 46, code job>\n<frame at 0x7ffd90266510, file \'test/test.py\', line 42, code foo>\n<frame at 0x7ffd902666a8, file \'test/test.py\', line 38, code bar>\n<frame at 0x7ffd90266840, file \'test/test.py\', line 34, code baz>\n<frame at 0x7ffd90269388, file \'test/test.py\', line 30, code leaf>\n<frame at 0x7ffd9025f9f8, file \'/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/asyncio/tasks.py\', line 568, code sleep>\n<_asyncio.FutureIter object at 0x7ffd90239f18>: \'_asyncio.FutureIter\' object has no attribute \'cr_frame\'\n\n---- task\n<frame at 0x7ffd90080808, file \'test/test.py\', line 50, code work>\n<_asyncio.FutureIter object at 0x7ffd90239e58>: \'_asyncio.FutureIter\' object has no attribute \'cr_frame\'\n```\n\n#### Mailing list reference\n\nhttps://mail.python.org/archives/list/async-sig@python.org/thread/6E2LRVLKYSMGEAZ7OYOYR3PMZUUYSS3K/\n\n\n#### Original post dump\n\nHi group,\n\nI\'m recently debugging a long-running asyncio program that appears to\nget stuck about once a week.\n\nThe tools I\'ve discovered so far are:\nhigh level: `asyncio.all_tasks()` + `asyncio.Task.get_stack()`\nlow level: `loop._selector._fd_to_key`\n\nWhat\'s missing is the middle level, i.e. stack-like linkage of what is\nwaiting for what. For a practical example, consider:\n\n```py\nasync def leaf(): await somesocket.recv()\nasync def baz(): await leaf()\nasync def bar(): await baz()\nasync def foo(): await bar()\nasync def job(): await foo()\nasync def work(): await asyncio.gather(..., job())\nasync def main(): asyncio.run(work())\n```\n\nThe task stack will contain:\n* main and body of work with line number\n* job task with line number pointing to foo\n\nThe file descriptor mapping, socket fd, `loop._recv()` and a `Future`.\n\nWhat\'s missing are connections `foo->bar->baz->leaf`.\nThat is, I can\'t tell which task is waiting for what terminal `Future`.\n\nIs this problem solved in some way that I\'m not aware of?\nIs there a library or external tool for this already?\n\nPerhaps, if I could get a list of all pending coroutines, I could\nfigure out what\'s wrong.\n\nIf no such API exists, I\'m thinking of the following:\n\n```py\nasync def foo():\n    await bar()\n\nIn [37]: dis.dis(foo)\n  1           0 LOAD_GLOBAL              0 (bar)\n              2 CALL_FUNCTION            0\n              4 GET_AWAITABLE\n              6 LOAD_CONST               0 (None)\n              8 YIELD_FROM\n             10 POP_TOP\n             12 LOAD_CONST               0 (None)\n             14 RETURN_VALUE\n```\n\nStarting from a pending task, I\'d get it\'s coroutine and:\n\nGet the coroutine frame, and if current instruction is `YIELD_FROM`,\nthen the reference to the awaitable should be on the top of the stack.\nIf that reference points to a pending coroutine, I\'d add that to the\n"forward trace" and repeat.\n\nAt some point I\'d reach an awaitable that\'s not a pending coroutine,\nwhich may be: another `Task` (I already got those), a low-level `Future`\n(can be looked up in event loop), an `Event` (tough luck, shoulda logged\nall `Event`\'s on creation) or a dozen other corner cases.\n\nWhat do y\'all think of this approach?\n\nThanks,\nD.\n',
    'author': 'Dima Tisnek',
    'author_email': 'dimaqq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'FIXME',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
