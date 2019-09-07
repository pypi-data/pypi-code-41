from distutils.core import setup

with open("README") as file:
    readme = file.read()


# setup(
#     name="test_game_private",
#     version="2.0.1",
#     packages=['modularize'],
#     url='http://localhost:8081/simple,
#     license='LICENSE.txt',
#     description='fantasy tut game private',
#     long_description=readme,
#     author='ja',
#     author_email="ja@email.com"
# )


setup(
    name="test_game",
    version="2.0.1",
    packages=['modularize'],
    url='https://testpypi.python.org/pypi/test_game/',
    license='LICENSE.txt',
    description='fantasy tut game',
    long_description=readme,
    author='ja',
    author_email="ja@email.com"
)
