import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cursetup", 
    version="0.0.1", 
    author="paperbenni", 
    author_email = "paperbenni@gmail.com", 
    description="avoid cursing at curses", 
    long_description=long_description, 
    long_description_content_type="text/markdown", 
    url="https://github.com/paperbenni/cursetup", 
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)