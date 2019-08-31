from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fcards',
    version='0.2.0',
    author="rzrshr",
    author_email="surplussinewaves@gmail.com",
    description="Digital flashcards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=find_packages(),
    python_requires='>=3.5',
    entry_points={
        'console_scripts': ['fcards=fcards.fcards:main'],
    },
    install_requires=[
        'windows-curses;platform_system=="Windows"'
],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
