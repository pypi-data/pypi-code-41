from setuptools import setup, find_packages

filepath = "uitable/README.md"

setup(
    name="uitable",
    version="0.0.1",
    description="display data by table format",
    long_description=open(filepath).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yxxhero/uitable",
    author="yxxhero",
    author_email="aiopsclub@163.com",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    zip_safe=False,
)
