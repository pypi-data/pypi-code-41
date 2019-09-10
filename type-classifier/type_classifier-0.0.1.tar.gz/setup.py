import setuptools

setuptools.setup(
    name="type_classifier",
    version="0.0.1",
    author='leowz',
    author_email='weng.zhang@icloud.com',
    description="ML classifier package",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_data={'': ['model_trained.sav']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
