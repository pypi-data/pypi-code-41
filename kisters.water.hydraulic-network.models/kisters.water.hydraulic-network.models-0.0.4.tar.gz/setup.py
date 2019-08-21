import setuptools

import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kisters.water.hydraulic-network.models",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jesse VanderWees",
    author_email="jesse.vanderwees@kisters-bv.nl",
    description="Model library for the Kisters Hydraulic Network Storage service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/kisters/water/hydraulic-network/models",
    packages=["kisters.water.hydraulic_network.models"],
    zip_safe=False,
    install_requires=["cerberus", "isodate"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
)
