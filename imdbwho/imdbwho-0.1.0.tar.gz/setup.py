from setuptools import setup
setup(
    name = 'imdbwho',
    version = '0.1.0',
    packages = ['imdbwho'],
    license='MIT',
    install_requires=[
        'beautifulsoup4'
    ],

    entry_points = {
        'console_scripts': [
            'imdbwho = imdbwho.__main__:main'
        ]
    })
