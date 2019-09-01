import setuptools

setuptools.setup(
    author="Sergio Pelissari",
    author_email="sonared@gmail.com",
    name="quantzbrapi",
    version="0.0.5",
    include_package_data=True,
    long_description_content_type="text/markdown",
    url="https://github.com/primehaxor/quantzbrapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=["requests", "pandas"],
)   