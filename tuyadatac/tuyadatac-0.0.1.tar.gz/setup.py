import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tuyadatac",
    version="0.0.1",
    author="fangdong",
    author_email="fangdong@tuya.com",
    description="A tuya data package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://registry.code.tuya-inc.top/datacenter/FTPServer.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
