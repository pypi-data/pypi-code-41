import setuptools

pkg_name = "reactopya_examples"

setuptools.setup(
    name=pkg_name,
    version="0.6.0",
    author="Jeremy Magland",
    description="Gallery of example reactopya widgets",
    packages=setuptools.find_packages(),
    scripts=[],
    include_package_data=True,
    install_requires=[
        'reactopya',
        'simplejson',
        'numpy',
        'mountaintools'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)