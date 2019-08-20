import json
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Get version from npm package.json file
pkg_version = None
with open('package.json') as fv:
    pkg_string = fv.read()
    pkg_object = json.loads(pkg_string)
    pkg_version = pkg_object.get('version')
    print('Read version string: {}'.format(pkg_version))

if pkg_version is None:
    raise RuntimeError('Unable to get version from package.json file')

# Set module version
with open('sidegears/version.py', 'w') as fs:
    fs.write('__version__ = \'{}\'\n'.format(pkg_version))

setuptools.setup(
    name="sidegears",
    version=pkg_version,
    author="john Tourtellott",
    author_email="john.turtle@gmail.com",
    description="Tools for browser-based desktop applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/john.tourtellott/sidegears",
    packages=setuptools.find_packages(),
    install_requires=[
        'jsonrpcserver',
        'websockets'
    ],
    package_data={'sidegears': [
        '../package.json',
        '../LICENSE',
        '../examples/pyside/*.*',
        '../examples/testbed/*.*',
        '../examples/webruntime/*.*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
    ],
)
