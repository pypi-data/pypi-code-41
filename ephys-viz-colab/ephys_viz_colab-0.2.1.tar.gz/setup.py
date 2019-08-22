import setuptools

pkg_name = "ephys_viz_colab"

setuptools.setup(
    name=pkg_name,
    version="0.2.1",
    author="Jeremy Magland",
    description="Neurophysiology visualization widgets",
    packages=setuptools.find_packages(),
    include_package_data=True,
    scripts=[],
    install_requires=[
        'reactopya==0.3.2',
        'simplejson',
        'jupyter',
        'numpy',
        'mountaintools',
        'spikeforest',
        'scipy'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)