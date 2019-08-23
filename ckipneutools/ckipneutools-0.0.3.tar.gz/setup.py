import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = "ckipneutools",
    version = "0.0.3",
    author = "Peng-Hsuan Li",
    author_email = "jacobvsdanniel@gmail.com",
    description = "Neural implementation of CKIPWS and CKIPNER",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jacobvsdanniel/ckipneutools",
    packages = ["ckipneutools"],
    package_dir = {"ckipneutools": "src"},
    extras_require = {
        "tf": ["tensorflow"],
        "tfgpu": ["tensorflow-gpu"],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
    ],
)
