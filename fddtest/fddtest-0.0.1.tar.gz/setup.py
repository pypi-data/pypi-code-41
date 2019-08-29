import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
        name = "fddtest",
        version = "0.0.1",
        author = "fdd",
        author_email = "1064540094@qq.com",
        description = "my first pip test",
        long_description = long_description,
        long_description_content_type = "text/markdown",
        url = "https://github.com/whu-dft/fddtest",
        packages = setuptools.find_packages(),
        classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
            ]
        )

