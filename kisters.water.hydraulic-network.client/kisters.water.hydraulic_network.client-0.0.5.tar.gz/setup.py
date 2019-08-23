import setuptools

import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kisters.water.hydraulic_network.client",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jesse VanderWees",
    author_email="jesse.vanderwees@kisters-bv.nl",
    description="Client library for the Kisters Hydraulic Network Storage service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/kisters/water/hydraulic-network/client",
    packages=["kisters.water.hydraulic_network.client"],
    zip_safe=False,
    install_requires=["kisters.water.hydraulic_network.models", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
)
