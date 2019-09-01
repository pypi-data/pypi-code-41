import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Golmorich',
    version='1.2.0.1',
    scripts=['golmorich.py'],
    author='Imtiaz Ahmed',
    author_email='imtiaz@imtiazahmed.dev',
    description='A simple text editor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://imtiazahmed.dev',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.0'
)