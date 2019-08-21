import setuptools
import sys
import hanime

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hanime-scraper",
    version="1.4.3",
    author="WorstGameDev",
    author_email="worstgamedev@gmail.com",
    description="A small commandline script for hanime community image scraping.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/worstgamedev/hanime-scraper",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['hanime = hanime.app_requests:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free For Educational Use",
        "Operating System :: OS Independent",
    ],
)