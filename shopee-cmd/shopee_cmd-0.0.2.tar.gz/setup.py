import setuptools

install_requires = ['Click']

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shopee_cmd",
    version="0.0.2",
    author="jiao.xue",
    author_email="jiao.xuejiao@gmail.com",
    description="Shopee command line tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/garena-shopee/cmd",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        hello=shopee_cmd.hello:hello
        import_bins=shopee_cmd.import_bins:run
    ''',
)
