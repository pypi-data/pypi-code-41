from distutils.core import setup

setup(
    name='pypack',
    version='1.0',
    author='anatoly techtonik <techtonik@gmail.com>',
    url='https://github.com/techtonik/pypack',

    description='Wrap Python module into executable .zip package.',
    license='Public Domain',

    py_modules=['pypack'],

    install_requires = '''

''',
    entry_points = {
        'console_scripts': ['pypack=pypack:main'],
    },

    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
