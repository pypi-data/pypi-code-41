import subprocess
import sys

from setuptools import find_packages, setup

__version__ = "1.1.1"


if sys.argv[-1] == "publish":
    subprocess.run("python setup.py sdist bdist_wheel".split())
    subprocess.run("twine upload dist/*".split())
    subprocess.run(
        ["git", "tag", "-a", f"v{__version__}", "-m", f"'Version {__version__}'"]
    )
    subprocess.run(["git", "push", "origin", "--tags"])
    sys.exit()


setup(
    name="maetema",
    version=__version__,
    description="Tema de MaeDocs",
    url="https://docs.maeorg.site",
    author="Ham Won Trikru",
    author_email="lwonderlich@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"maeguias.themes": ["mae = maetema"]},
)
