from setuptools import setup

setup(
    name='kewodict',
    version='0.1.1',
    py_modules=['main'],
    author='melon',
    author_email='melonchild@outlook.com',
    description='kewodict',
    install_requires=[
        "pymysql",
        "sqlalchemy"
    ],
    packages=['kewodict']
)