import os

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import setup

abs_path = os.path.dirname(os.path.abspath(__file__))
requirements_file = os.path.join(abs_path, 'requirements.txt')
install_requirements = parse_requirements(requirements_file, session=False)
requirements = [str(ir.req) for ir in install_requirements]

setup(
    name='gym_bit_flip',
    version='0.0.1',
    description='openai gym interface to bit flip problem described in Hindsight Experience Replay',
    author='Zach Dwiel',
    author_email='zach.dwiel@intel.com',
    license='Apache',
    packages=['gym_bit_flip'],
    install_requires=requirements,
)
