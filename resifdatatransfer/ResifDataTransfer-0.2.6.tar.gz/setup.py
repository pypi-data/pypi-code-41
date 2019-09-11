from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["ResifDataTransferTransaction"]

setup(
    name="ResifDataTransfer",
    version="0.2.6",
    author="RESIF",
    entry_points={
        "console_scripts": [
            "ResifDataTransfer=ResifDataTransfer.ResifDataTransfer:main"
        ]
    },
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.com/resif/resif-data-transfer',
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown; charset=UTF-8",
    data_files=[("resif_data_transfer/", ["ResifDataTransfer/ResifDataTransfer.conf"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
