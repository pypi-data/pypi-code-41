from setuptools import setup, find_packages
req = open('semvar/.req').read().splitlines()
setup(
    name='semvar',
    packages=find_packages(),
    version='0.2.3',
    include_package_data=True,
    description='semvar',
    author='Ryumejin',
    author_email='ryumejin@gmail.com',
    install_requires=req,
    entry_points={
        'console_scripts': [
            'semvar=semvar.console:main'
        ]
    }
)
