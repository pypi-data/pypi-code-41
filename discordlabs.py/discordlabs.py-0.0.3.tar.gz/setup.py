from setuptools import setup

from discordlabspy import __title__, __author__, __version__

if not __title__:
    raise RuntimeError('title is not set')
if not __author__:
    raise RuntimeError('author is not set')
if not __version__:
    raise RuntimeError('version is not set')

with open("requirements.txt", "r") as f:
    requirements = f.readlines()

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name=__title__,
    author=__author__,
    url="https://github.com/discordbotcord/Python-Library",
    version=__version__,
    packages=['discordlabspy'],
    python_requires=">= 3.5",
    include_package_data=True,
    install_requires=requirements,
    description="A simple API wrapper for Discord Labs.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="api wrapper discord bot bots botlist labs discordlabs discordbotlabs ",
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ),
    project_urls={
        'Support': 'https://discord.gg/SMpSzuX',
        'Source': 'https://github.com/discordbotcord/Python-Library',
    },
)