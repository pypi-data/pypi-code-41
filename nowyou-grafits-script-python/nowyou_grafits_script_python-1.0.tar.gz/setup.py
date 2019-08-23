"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#    long_description = f.read()

setuptools.setup(
    name="nowyou_grafits_script_python",
    version="1.0",
    description="Now you project grafis scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://bitbucket.org/inventilabs/nowyou-grafis-script-python/",
    # Author details
    author="Alex Mensak",
    author_email="alexander.mensak@ilabs.cz",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
    ],
    keywords="nowyou python",
    packages=setuptools.find_packages(),
    install_requires=["pyautogui",],
    python_requires=">=3.6",
    # extras_require={"dev": ["pytest"]},
)