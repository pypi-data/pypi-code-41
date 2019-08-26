import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ml_boilerplate',
    version='0.2',
    author="Jack Bicknell",
    author_email="jakbicknell@gmail.com",
    description="A collection of useful tools for machine learning.",
    long_description_content_type="text/markdown",
    url="https://github.com/jackbicknell14/ml-boilerplate",
    packages=setuptools.find_packages(),
    install_requires=[
        'scikit-learn',
        'pandas',
        'xgboost',
        'numpy',
        'scipy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
