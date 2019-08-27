from pathlib import Path
from setuptools import setup, find_packages


def make_long_description():
    here = Path(__file__).parent
    readme = (here / "README.md").read_text()
    return f"{readme}\n\n"


setup(
    name="py3status-omegav",
    version="0.1.1",
    description="py3status module to check door status at Omega Verksted",
    long_description=make_long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    install_requires=["py3status>=3.20", "requests"],
    package_dir={"": "src"},
    entry_points={"py3status": ["module = py3status_omegav.omegav"]},
    url="https://github.com/jakoblover/py3status-omegav",
    classifiers=[
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],

)
