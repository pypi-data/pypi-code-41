from setuptools import setup


# include __about__.py.
about = {}
with open('torchwood.py') as f:
    exec(f.read(), about)


setup(
    name='torchwood',
    version=about['__version__'],
    author='Heungsub Lee',
    platforms='any',
    py_modules=['torchwood'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Typing :: Typed',
    ],
)
