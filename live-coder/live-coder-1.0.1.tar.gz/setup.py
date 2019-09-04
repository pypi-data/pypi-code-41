import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="live-coder",
    version="1.0.1",
    author="Fraser Greenlee",
    author_email="frassyg@gmail.com",
    description="Server for Live Coder, works with the Live Coder VSCode extension.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Fraser-Greenlee/live-coding/tree/server",
    packages=['live_coder'],
    install_requires=[
        'astor == 0.8.0',
        'flask == 1.0.2',
        'yapf == 0.27.0',
        'pygments == 2.4.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
