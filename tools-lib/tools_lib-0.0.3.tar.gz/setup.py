from setuptools import setup, find_packages

with open("README.md", "r") as readMe:
    longDesc = readMe.read()

setup(
    name="tools_lib",
    packages=find_packages(),
    version="0.0.3",
    license="AGPL 3.0",
    description="An integrative library that contains miscellaneous tools for performing various type of options.",
    long_description=longDesc,
    long_description_content_type="text/markdown",
    include_package_data=True,
    author="Yogesh Aggarwal",
    author_email="developeryogeshgit@gmail.com",
    url="https://github.com/yogesh-aggarwal/tools-lib",
    download_url="https://raw.githubusercontent.com/yogesh-aggarwal/tools-lib/master/dist/tools_lib-0.0.3.tar.gz",
    keywords=["Miscellaneous tools", "Useful"],
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
