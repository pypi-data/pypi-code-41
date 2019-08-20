# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['abridge']

package_data = \
{'': ['*']}

install_requires = \
['enlighten>=1.3,<2.0',
 'moviepy>=1.0,<2.0',
 'numpy>=1.17,<2.0',
 'proglog>=0.1.9,<0.2.0']

entry_points = \
{'console_scripts': ['abridge = abridge.cli:main']}

setup_kwargs = {
    'name': 'abridge',
    'version': '0.1.2',
    'description': 'Splice similar frames from videos',
    'long_description': '# abridge\n\n[![pipeline status](https://gitlab.com/freshollie/abridge/badges/master/pipeline.svg)](https://gitlab.com/freshollie/abridge/commits/master)\n[![coverage report](https://gitlab.com/freshollie/abridge/badges/master/coverage.svg)](http://freshollie.gitlab.io/abridge)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n\nEffortlessly shorten videos.\n\n## About\n\n`abridge` can automatically shorten video files by removing parts from the video\nwhere not much happens. This is great for making timelapse videos more engaging\nand removes the need for manual editing to cut these dead spots from the videos.\n\n## Installation\n\n`pip install abridge`\n\n`abridge` makes use of `moviepy`, which releys on `ffmpeg`. `ffmpeg` should be installed\nwhen the package is installed, but this may not work on some systems.\n\n## Docker\n\n`adbridge` can be run as a docker image, which gaurentees it will run\non all systems.\n\n`docker pull freshollie/abridge:latest`\n\n`docker run freshollie/abridge`\n\n## Usage\n\n```\nusage: abridge [-h] [-w workers] [-o outdir] [-t diff-threshold]\n               [-r repetition-threshold]\n               clip [clip ...]\n\nEffortlessly shorten videos\n\npositional arguments:\n  clip                  Clip to cut or glob group\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -w workers            Number of clip processors\n  -o outdir\n  -t diff-threshold     Difference threshold required between frames for a\n                        frames to be considered different\n  -r repetition-threshold\n                        Number of frames in a row required to make a cut\n```\n\n## Api\n\n```python\nfrom abridge import abridge_clip\n\nabridge_clip("/path/to/clip")\n```\n\n## Developing\n\nThe `abridge` project is managed and packaged by `poetry`\n\nUse `poetry install` to download the required packages for development\n\n`poetry run pre-commit install` should be run to install the pre-commit\nscripts which help with ensuring code is linted before push.\n\n### Tests\n\nTests are written with `pytest` and can be run with `make test`\n\n### Linting\n\n`abridge` is linted with `pylint` and formatted with `black` and `isort`\n\n`mypy` is used throughout the project to ensure consitent types.\n\n`make lint` will check linting, code formatting, and types\n\n`make format` will format code to required standards\n\n## TODO:\n\n- Test coverage on processor\n\n## License\n\n`MIT`\n',
    'author': 'Oliver Bell',
    'author_email': 'freshollie@gmail.com',
    'url': 'https://github.com/sdispater/poetry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
