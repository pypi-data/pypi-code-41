# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pybotics']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.0', 'numpy>=1.9', 'scipy>=1.0']

setup_kwargs = {
    'name': 'pybotics',
    'version': '0.7.0',
    'description': 'Python Toolbox for Robotics',
    'long_description': '# ![](https://raw.githubusercontent.com/nnadeau/pybotics/master/media/robotic-arm.png) pybotics\n\nThe Python Toolbox for Robotics\n\n|Component|Badges|\n|---|---|\n| GitHub | [![GitHub issues](https://img.shields.io/github/issues/nnadeau/pybotics.svg)](https://github.com/nnadeau/pybotics/issues) [![GitHub forks](https://img.shields.io/github/forks/nnadeau/pybotics.svg)](https://github.com/nnadeau/pybotics/network) [![GitHub stars](https://img.shields.io/github/stars/nnadeau/pybotics.svg)](https://github.com/nnadeau/pybotics/stargazers) [![GitHub tag](https://img.shields.io/github/tag/nnadeau/pybotics.svg?maxAge=2592000?style=flat-square)](https://github.com/nnadeau/pybotics/releases) |\n| PyPI | [![PyPI Version](https://img.shields.io/pypi/v/pybotics.svg)](https://pypi.python.org/pypi/pybotics) [![PyPI License](https://img.shields.io/pypi/l/pybotics.svg)](https://pypi.python.org/pypi/pybotics) [![PyPI Wheel](https://img.shields.io/pypi/wheel/pybotics.svg)](https://pypi.python.org/pypi/pybotics) [![PyPI Format](https://img.shields.io/pypi/format/pybotics.svg)](https://pypi.python.org/pypi/pybotics) [![PyPI Pythons](https://img.shields.io/pypi/pyversions/pybotics.svg)](https://pypi.python.org/pypi/pybotics) [![PyPI Implementation](https://img.shields.io/pypi/implementation/pybotics.svg)](https://pypi.python.org/pypi/pybotics) |\n| CI | [![Build Status](https://travis-ci.org/nnadeau/pybotics.svg?branch=master)](https://travis-ci.org/nnadeau/pybotics) |\n| Coverage | [![codecov](https://codecov.io/gh/nnadeau/pybotics/branch/master/graph/badge.svg)](https://codecov.io/gh/nnadeau/pybotics) |\n\n## Usage\n\n### Installation\n\n```bash\n# python3 is mapped to pip or inside a venv\npip install pybotics\n\n# python3-pip\npip3 install pybotics\n\n# https://github.com/pypa/pipenv\npipenv install pybotics\n\n# https://github.com/sdispater/poetry\npoetry add pybotics\n```\n\n### Applications & Examples\n\n- [Basic Usage](examples/basic_usage.py)\n- [Kinematics](examples/kinematics.ipynb)\n- [Calibration](examples/calibration.ipynb)\n- Trajectory and path planning\n- Machine learning\n\n## Featured In\n\n- [Impedance Control Self-Calibration of a Collaborative Robot Using Kinematic Coupling](https://www.mdpi.com/2218-6581/8/2/33/htm)\n- [PyCon Canada 2017](https://2017.pycon.ca/schedule/53/)\n  - [Talk Photos](https://500px.com/nicholasnadeau/galleries/pycon-canada-2017)\n  - [Slides](https://github.com/nnadeau/pycon-canada-2017)\n- [Montreal-Python 2017](https://www.youtube.com/watch?v=wgKoGA69YXQ)\n\n## Citing\n\n- Please cite the following articles if you use `pybotics` in your research:\n\n> Nadeau, Nicholas A., Ilian A. Bonev, and Ahmed Joubair. "Impedance Control Self-Calibration of a Collaborative Robot Using Kinematic Coupling." Robotics 8.2 (2019): 33.\n\n```\n@article{nadeau2019impedance,\n  title={Impedance Control Self-Calibration of a Collaborative Robot Using Kinematic Coupling},\n  author={Nadeau, Nicholas A and Bonev, Ilian A and Joubair, Ahmed},\n  journal={Robotics},\n  volume={8},\n  number={2},\n  pages={33},\n  year={2019},\n  publisher={Multidisciplinary Digital Publishing Institute}\n}\n```\n\n## Development\n\n- Install dev virtual environment:\n\n```bash\npoetry install\n```\n\n- Make changes\n- Submit a PR\n\n---\n\n<div>Logo made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="http://www.flaticon.com" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>\n',
    'author': 'Nicholas Nadeau',
    'author_email': 'nicholas.nadeau@gmail.com',
    'url': 'https://github.com/nnadeau/pybotics',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
