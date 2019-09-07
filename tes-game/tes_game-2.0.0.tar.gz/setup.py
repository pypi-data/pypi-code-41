from distutils.core import setup

with open("README") as file:
    readme = file.read()


setup(
    name="tes_game",
    version="2.0.0",
    packages=['modularize'],
    url='https://testpypi.python.org/pypi/tes_game/',
    license='LICENSE.txt',
    description='fantasy tut game',
    long_description=readme,
    author='ja',
    author_email="ja@email.com"
)