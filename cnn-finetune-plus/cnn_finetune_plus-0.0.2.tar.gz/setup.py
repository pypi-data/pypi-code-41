import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
install_requires = [
    #'numpy>=1.11.1',
    #'pandas>=0.19.0'
    'requests',
    'torch',
    'cnn_finetune',
]
setuptools.setup(
    name="cnn_finetune_plus",
    version="0.0.2",
    author="X",
    author_email="X@X.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
)