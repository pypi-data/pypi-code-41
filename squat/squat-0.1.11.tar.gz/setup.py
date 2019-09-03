import setuptools


try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]


setuptools.setup(
    name='squat',
    version='0.1.11',
    scripts=[],
    author="Binay Kumar Ray",
    author_email="binayray2009@gmail.com",
    description="SQUAT",
    long_description='spend quality and usage analysis tool',
    long_description_content_type="text/markdown",
    url="https://github.com/binayr/SQUAT.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)