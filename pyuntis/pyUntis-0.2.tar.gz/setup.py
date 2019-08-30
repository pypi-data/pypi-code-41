import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name="pyUntis",
                 version="0.2",
                 description="Python parser for Untis substitution tables",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/sn0wmanmj/pyUntis",
                 author="Moritz Jannasch",
                 author_email="contact@moritzj.de",
                 license="MIT",
                 packages=setuptools.find_packages(),
                 install_requires=[
                     "bs4",
                     "lxml"
                 ],
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 )
