from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='MaLeSMo',
    version='0.2.7',
    author="Denis Moshensky",
    author_email="loven7doo@gmail.com",  
    description="Machine Learning Standard Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loven-doo/MaLeSMo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    package_data={},
    install_requires=[
        'numpy >= 1.15.1',
        'pandas >= 0.23.4',
        'scipy >= 1.1.0',
        'dill >= 0.2.9',
        'malemba >= 0.4.5',
        'catboost >= 0.12.2',
        'xgboost >= 0.81',
        'jsondler >= 0.0.1'
    ],
    entry_points={
        'console_scripts': []
    }
)
