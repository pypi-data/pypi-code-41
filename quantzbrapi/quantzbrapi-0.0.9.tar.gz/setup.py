import setuptools

setuptools.setup(
    author="Sergio Pelissari",
    author_email="sonared@gmail.com",
    name="quantzbrapi",
    version="0.0.9",
    long_description_content_type="text/markdown",
    url="https://github.com/primehaxor/quantzbrapi",
    packages=['quantzbrapi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=["requests", "pandas"],
)   
