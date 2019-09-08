import setuptools

pkg_name = "ephys_viz"

setuptools.setup(
    name=pkg_name,
    version="0.5.3",
    author="Jeremy Magland",
    description="Neurophysiology visualization widgets",
    packages=setuptools.find_packages(),
    scripts=[],
    include_package_data=True,
    install_requires=[
        'reactopya',
        'simplejson',
        'jupyter',
        'numpy',
        'mountaintools',
        'spikeforest',
        'scipy',
        'vtk',
        'imageio',
        'imageio-ffmpeg'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)