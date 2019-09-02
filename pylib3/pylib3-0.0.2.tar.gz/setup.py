from setuptools import setup
import pylib3

with open("README.md") as ifile:
    long_description = ifile.read()

package_name = 'pylib3'
setup(
    name=package_name,
    version=pylib3.get_version(
        caller=__file__,
        version_file='{}_VERSION'.format(package_name.upper())
    ),
    include_package_data=True,
    packages=[package_name],
    install_requires=[
        'termcolor==1.1.0'
    ],
    scripts=[],
    url='https://gitlab.com/shlomi.ben.david/pylib3',
    author='Shlomi Ben-David',
    author_email='shlomi.ben.david@gmail.com',
    description='Python Shared Library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
