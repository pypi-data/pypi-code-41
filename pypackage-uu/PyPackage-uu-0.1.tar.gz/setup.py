from distutils.core import setup

setup(
    name="PyPackage-uu",
    packages=["PyPackage-u"],
    version="0.1",
    license="MIT",
    description="Just a demo case for uploading pypi package to pypi repository",
    author="shady",  # Type in your name
    author_email="darkercookies@gmail.com",
    url="https://github.com/shady-robot",
    download_url="https://github.com/shady-robot/PyPi-Workflow/archive/0.1.tar.gz",  # I explain this later on
    keywords=["PyPi", "Demo", "Test"],  # Keywords that define your package best
    install_requires=["validators", "beautifulsoup4"],  # I get to this in a second
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3",  # Specify which pyhton versions that you want to support
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
