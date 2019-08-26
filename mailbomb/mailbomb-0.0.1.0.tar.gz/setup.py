from setuptools import setup, find_packages

setup(
    name='mailbomb',
    version='0.0.1.0',
    packages=find_packages(),
    license='GPLv3',
    description='A python package to send corporate amounts of email quickly and easily',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/D3PSI/mailbomb',
    author='D3PSI',
    author_email='d3psigames@gmail.com',
    install_requires=[
      ],
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: OS Independent",
     ],
)