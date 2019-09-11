from setuptools import setup

setup(
    name='array_range',
    version='1.0',
    author='Ahmed Fasih',
    author_email='ahmed@aldebrn.me',
    description="Generate tuples of slices to easily iterate on non-overlapping sub-arrays of multdimensional arrays",
    license='Unlicense',
    url='https://github.com/fasiha/array_ranges',
    py_modules=['array_range'],
    test_suite='nose.collector',
    tests_require=['nose', 'numpy'],
    zip_safe=True,
)
