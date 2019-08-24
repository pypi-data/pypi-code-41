import setuptools

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pactverify",
    version="1.7.2",
    author="liuhui",
    author_email="1318633361@qq.com",
    description="接口断言契约校验",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xglh/PactVerify_demo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)