import codecs
import os

from pkg_resources import parse_requirements
from setuptools import find_packages, setup


def read(file_name):
    pkg_root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(pkg_root_dir, file_name)
    assert os.path.isfile(file_path), f'setup.py cannot open not existing file: {file_path}'
    with codecs.open(file_path, encoding='utf-8') as file_:
        return file_.read()


def get_requirements():
    return [str(r) for r in parse_requirements(read('requirements.txt'))]


setup(
    name='yamliz',
    author="Michał Kaczmarczyk",
    author_email="michal.s.kaczmarczyk@gmail.com",
    url='https://gitlab.com/kamichal/yamliz',
    description='Dataclasses married with yaml.',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=get_requirements(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    keywords='',
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
)
