import setuptools

pkg_name = "ephys_viz_jup"

setuptools.setup(
    name=pkg_name,
    version="0.2.6",
    author="Jeremy Magland",
    description="Neurophysiology visualization widgets",
    packages=setuptools.find_packages(),
    scripts=[],
    install_requires=[
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