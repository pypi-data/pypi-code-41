import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-pie",
    version="1.0.1",
    author="kerol",
    author_email="ikerol@163.com",
    description="Collections to speed up django development in several minutes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kerol/django-pie",
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.6',
    ),
    install_requires=[
        'django>=2.2.5',
        'redis>=3.3.8',
        'pycryptodome>=3.9.0',
    ]
)