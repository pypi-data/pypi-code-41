import setuptools

with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="greendeck-logging",
    version="0.0.7",
    author="abhay kumar",
    author_email="abhay.kumar@greendeck.co",
    description="Greendeck logging package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhay-kum/greendeck-logging.git",
    packages=['greendeck_logging'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'elasticsearch'
    ],
    include_package_data=True,
    zip_safe=False
)
