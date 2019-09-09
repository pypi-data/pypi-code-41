# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['subby']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'subby',
    'version': '0.1.2',
    'description': 'Subprocesses simplified',
    'long_description': '[![Travis CI](https://travis-ci.org/jdidion/subby.svg?branch=master)](https://travis-ci.org/jdidion/subby)\n[![Code Coverage](https://codecov.io/gh/jdidion/subby/branch/master/graph/badge.svg)](https://codecov.io/gh/jdidion/subby)\n\nSubby is a small Python library with the goal of simplifying the use of subprocesses.\n\nSubby was inspired by [delegator.py](https://github.com/amitt001/delegator.py), but it adds a few additional features and excludes others (e.g. no `pexpect` support). Subby was originally written as part of the [dxpy.sugar](https://github.com/dnanexus/dx-toolkit/tree/SCI-1321_dx_sugar/src/python/dxpy/sugar) package, but because it is (hopefully) useful more generally, it is being made available as a separate package.\n\n## Requirements\n\nThe only requirement is python 3.6+. There are no other 3rd-party runtime dependencies. The `pytest` and `coverage` packages are required for testing.\n\n## Installation\n\n`pip install subby`\n\n## Usage\n\nSubby\'s primary interface is the `run` function. It takes a list of commands and executes them. If there is are multiple commands, they are chained (i.e. piped) together.\n\n```python\nimport subby\n\n# We can pass input to the stdin of the command as bytes\ninput_bytes = b"foo\\nbar"\n\n# The following three commands are equivalent; each returns a\n# `Processes` object that can be used to inspect and control\n# the process(es).\np1 = subby.run([["grep foo", "wc -l"]], stdin=input_bytes)\np2 = subby.run(("grep foo", "wc -l"), stdin=input_bytes)\np3 = subby.run("grep foo | wc -l", stdin=input_bytes)\n\n# The `done` property tells us whether the processes have finished\nassert p1.done and p2.done and p3.done\n\n# The `output` property provides the output of the command\nassert p1.output == p2.output == p3.output == b"1"\n```\n\nBy default, the `run` function blocks until the processes are finshed running. This behavior can be changed by passing `block=False`, in which case, the caller is responsible for checking the status and/or calling the `Processes.block()` method manually.\n\n```python\nimport subby\nimport time\n\np = subby.run("sleep 10", block=False)\nfor i in range(5):\n    if p.done:\n        break\n    else:\n        time.sleep(1)\nelse:\n    # A timeout can be used to kill the process if it doesn\'t\n    # complete in a certain amount of time. By default, block()\n    # raises an error if the return code is non-zero.\n    p.block(timeout=10, raise_on_error=False)\n    \n    # The process can also be killed manually.\n    p.kill()\n\n# The `Processes.ok` property is True if the processes have\n# finished and the return code is 0.\nif not p.ok:\n    # The `Processes.output` and `Processes.error` properties\n    # provide access to the process stdout and stderr.\n    print(f"The command failed: stderr={p.error}")\n```\n\nSubby supports several different types of arguments for stdin, stdout, and stderr:\n\n* A file: specified as a `pathlib.Path`; for stdin, the content is read from the file, whereas for stdout/stderr the content is written to the file (and is thus not available via the `output`/`error` properties).-->\n* A bytes string: for stdin, the bytes are written to a temporary file, which is passed to the process stdin.\n* One of the values provided by the `StdType` enumeration:\n    * PIPE: for stdout/stderr, `subprocess.PIPE` is used, giving the caller direct access to the process stdout/stderr streams.\n    * BUFFER: for stdout/stderr, a temporary file is used, and the contents are made available via the `output`/`error` properties after the process completes.\n    * SYS: stdin/stdout/stderr is passed through from the main process (i.e. the `sys.stdin/sys.stdout/sys.stderr` streams).\n',
    'author': 'John Didion',
    'author_email': 'github@didion.net',
    'url': 'https://github.com/jdidion/subby',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
