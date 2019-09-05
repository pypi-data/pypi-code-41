import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="ValidationTool",
    version="1.0.0",
    description="Fitch Ratings MVG Validation Tool for criteria models",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/siyuan-columbia/FitchValidationTool",
    author="Siyuan Li",
    author_email="siyuan.li@fitchratings.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
#    include_package_data=True,
#    install_requires=[],
#    entry_points={
#        "console_scripts": [
#            "realpython=reader.__main__:main",
#        ]
#    },
)