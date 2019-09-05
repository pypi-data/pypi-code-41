import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apiguard",
    version="0.0.1",
    author="Erdem Aybek",
    author_email="eaybek@gmail.com",
    description=" ".join(["alone oauth2 server"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaybek/seperator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
    python_requires=">=3.6",
)
