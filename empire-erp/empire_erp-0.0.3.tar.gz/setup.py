import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="empire_erp",
    version="0.0.3",
    author="Vladimir Nomkhoev",
    author_email="n_vova@mail.ru",
    description="Empire ERP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nomhoi/empire-erp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)