from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    version='0.0.1',
    name='lscloud',
    packages=['lscloud'],
    description='A python utility that display cloud resource avialablity',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tony Vattathil',
    author_email='avattathil@gmail.com',
    url='https://avattathil.github.io/lscloud',
    license='Apache License 2.0',
    download_url='https://github.com/avattathil/lscloud/tarball/master',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Operating System :: POSIX :: Linux',
    ],
    scripts=[
        'bin/lscloud'
    ],
    keywords=['aws', 'lscloud'],
    install_requires=required,
#    test_suite="tests",
#    tests_require=["mock", "boto3"],
    include_package_data=True
)
