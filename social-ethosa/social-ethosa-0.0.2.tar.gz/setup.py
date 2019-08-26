import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="social-ethosa",
    version="0.0.2",
    author="Ethosa",
    author_email="social.ethosa@gmail.com",
    description="The social ethosa library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SakiKawasaki/social_ethosa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)