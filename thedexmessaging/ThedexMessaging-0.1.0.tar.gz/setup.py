import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setuptools.setup(
    name="ThedexMessaging",
    version="0.1.0",
    author="Kai Reichart",
    author_email="kai@reichart.dev",
    description="A Package to create Messages for the Thedex Messaging API",
    long_description="[See the GitHub Page for more Details](https://github.com/KaiReichart/Thedex_Messaging.py)",
    long_description_content_type="text/markdown",
    url="https://github.com/KaiReichart/Thedex_Messaging.py",
    download_url="https://github.com/KaiReichart/Thedex_Messaging.py/archive/v0.1.0.tar.gz",
    packages=setuptools.find_packages(),
    install_requires=[
          'datetime',
      ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
