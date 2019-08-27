
from pathlib import Path
from setuptools import setup, find_packages

with Path('README.md').open() as f:
    long_description = f.read()

setup(
    name='i3pie',
    version="1.0",
    description='IPC library for i3wm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gcmt/i3pie',
    author='Giacomo Comitti',
    author_email='dev@gcomit.com',
    python_requires='>=3.6',
    packages=find_packages(),
    license='MIT',
    keywords='i3 i3wm',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
