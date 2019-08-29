import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()
with open("peertube_uploader/VERSION", "r") as fh:
    VERSION = fh.read().strip()

ret = setuptools.setup(
    name="peertube-uploader",
    version=VERSION,
    author="LoveIsGrief",
    author_email="loveisgrief@tuta.io",
    description="A script to make uploading to peertube instances easier.",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/NamingThingsIsHard/media_tools/peertube-uploader",
    packages=setuptools.find_packages(),
    package_data={
        "peertube_uploader": ["VERSION"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    project_urls={
        "Bug Tracker": "https://gitlab.com/NamingThingsIsHard/media_tools/peertube-uploader/issues",
    },
    entry_points={
        'console_scripts': [
            'ptu = peertube_uploader.main:main',
        ]
    }
)
