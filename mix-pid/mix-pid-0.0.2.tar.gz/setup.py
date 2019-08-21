import setuptools
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='mix-pid',
    version='0.0.2',
    description='锅炉压力的PID控制算法',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/xiangyangkan/pid',
    author='xiangyangkan',
    author_email='xiangyangkan@outlook.com',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='pid controller control',
    packages=setuptools.find_packages(),
    project_urls={
        'Documentation': 'https://mix-pid.readthedocs.io/',
    },
)
