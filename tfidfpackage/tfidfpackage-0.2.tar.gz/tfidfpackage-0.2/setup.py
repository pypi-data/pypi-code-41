from setuptools import find_packages, setup

setup(
    name="tfidfpackage",      # name of PyPI package
    version='0.2',          # version number, update with new releases
    packages= find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='Term frequency inverse document frequency',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
