import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytelebot",
    version="0.0.1",
    author="Alex Zaharchuk",
    author_email="olekmay@gmail.com",
    description="Python Telegram bot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexZaharchuk/pytelebot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)