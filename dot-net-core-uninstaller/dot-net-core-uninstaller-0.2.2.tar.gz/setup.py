import codecs
import os
from setuptools import setup

from dot_net_core_uninstaller import __version__

here = os.path.abspath(os.path.dirname(__file__)) + os.sep


def get_requirements(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read().splitlines()


setup(
    name='dot-net-core-uninstaller',
    version=__version__,
    install_requires=get_requirements('requirements.txt'),
    packages=['dot_net_core_uninstaller'],
    url='https://github.com/akshaybabloo/uninstall-dot-net-core',
    license='MIT',
    author='Akshay Raj Gollahalli',
    author_email='akshay@gollahalli.com',
    description='Delete previous versions of .Net Core and its runtime files.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords=['uninstaller', '.net core uninstaller', '.net core'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'dotnetcore = dot_net_core_uninstaller.cli:cli'
        ]
    }
)
