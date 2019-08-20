from setuptools import setup, find_packages


setup(
    name="interruptingboar",
    use_scm_version=True,
    url="https://github.com/dexter2206/interruptingboar",
    platforms=["Linux", "Unix", "Windows"],
    packages=find_packages(),
    author="Konrad Jałowiecki",
    author_email="dexter2206@gmail.com",
    setup_requires=["setuptools_scm"]
)