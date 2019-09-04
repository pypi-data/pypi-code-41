from setuptools import setup, find_packages

setup(
    name='git_dependency_python',
    version='1.1.1',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    packages=find_packages(),
    description='SDK that helps to manage dependencies directly from git repositories.',
    include_package_data=True,
    install_requires=[],
    author='Laimonas Sutkus',
    author_email='laimonas.sutkus@gmail.com',
    keywords='Git Python Dependency Manager',
    url='https://github.com/laimonassutkus/GitDependencyPython.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
)
