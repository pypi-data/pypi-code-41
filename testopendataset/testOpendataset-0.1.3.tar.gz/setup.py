from setuptools import setup
from setuptools import find_packages
 
setup(
    name='testOpendataset',
    version='0.1.3',
    description='SDK for the Open Image Dataset.',
    packages= find_packages(),
    author='zhenwan,t-tozho,t-zhiwan',
    author_email= "zhenwan@microsoft.com,t-tozho@microsoft.com,t-zhiwan@microsoft.com",
    url='https://dev.azure.com/zhenwan/zhenwan_default/_git/AMLProjects',
    install_requires=[
        'azureml-telemetry',
        'azure-storage-blob',
        'multimethods>=1.0.0',
        "numpy>=1.17.0",
        "pandas>=0.24.0",
        'pyspark>=2.4.3',
        'matplotlib >= 3.0.3',
        'opencv-contrib-python >= 4.0.25',
        'spacy>=2.1.8'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
