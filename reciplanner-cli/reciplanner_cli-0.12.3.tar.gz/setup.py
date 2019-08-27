import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='reciplanner_cli',
    description='Assists in managing recipes and items in kitchen',
    url='https://github.com/iron-condor/Reciplanner-CLI',
    author='iron-condor',
    author_email='christiandloftis@gmail.com',
    license='GPL-3.0',
    packages=['reciplanner_cli'],
    install_requires=[
        'pint'
    ],
    version='0.12.3',
    zip_safe=False
)
