import setuptools
from setuptools import setup

def readme():
    with open('README.md') as f:
        README=f.read()
    return README    

setuptools.setup(
    name="tuesday",
    version="3.0.0",
    author="OSD999",
    author_email="osdev99@gmail.com",
    description="A python package for automation",
    long_description=readme() ,
    long_description_content_type="text/markdown",
    url="https://github.com/om9999/Tuesday",
    
    python_requires='>=3',
    install_requires=['selenium','wikipedia','pyttsx3','speechRecognition','requests','PyAudio','geocoder',],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
   
)