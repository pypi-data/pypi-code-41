import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mailroom",
    version="0.0.1",
    author="Michael Strenk",
    description="Toolkit to generate & distribute html email reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MikeStrenk/mailroom",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6"
    ],
    install_requires=['exchangelib', 'jinja2'])
