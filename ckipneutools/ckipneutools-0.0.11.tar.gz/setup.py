import setuptools

setuptools.setup(
    name = "ckipneutools",
    version = "0.0.11",
    author = "Peng-Hsuan Li",
    author_email = "jacobvsdanniel@gmail.com",
    description = "DEPRECATED, please shift to install and import 'ckiptagger'",
    long_description = "DEPRECATED, please shift to install and import 'ckiptagger'",
    long_description_content_type = "text/plain",
    url = "https://github.com/ckiplab/ckiptagger",
    packages = ["ckipneutools"],
    package_dir = {"ckipneutools": "src"},
    install_requires = ["ckiptagger"],
    extras_require = {
        "tf": ["tensorflow"],
        "tfgpu": ["tensorflow-gpu"],
        "gdown": ["gdown"],
    },
    licence = "CC BY-NC-SA 4.0",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
    ],
)
