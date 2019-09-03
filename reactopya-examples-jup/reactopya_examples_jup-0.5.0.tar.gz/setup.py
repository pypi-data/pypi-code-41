import setuptools

pkg_name = "reactopya_examples_jup"

setuptools.setup(
    name=pkg_name,
    version="0.5.0",
    author="Jeremy Magland",
    description="Gallery of example reactopya widgets",
    packages=setuptools.find_packages(),
    scripts=[],
    include_package_data=True,
    install_requires=[
        'reactopya',
        'simplejson',
        'jupyter',
        'numpy',
        'mountaintools'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)