from setuptools import setup
from pathlib import Path

with open("README.md") as f:
    readme_text = f.read()

package_dir = "src"
package = "pupil_pthreads_win"

package_data = [
    str(match.resolve())
    for match in (Path() / package_dir / package / "data").rglob("*")
    if match.is_file()
]

setup(
    name="pupil-pthreads-win",
    description="A precompiled version of pthreads-win.",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    version="0.dev1",
    url="https://github.com/pupil-labs/pupil-pthreads-win",
    license="MIT License",
    author="Pupil Labs GmbH",
    author_email="pypi@pupil-labs.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[package],
    package_dir={"": package_dir},
    package_data={package: package_data},
)
