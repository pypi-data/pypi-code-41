import setuptools

with open ( "README.md" , "r" ) as fh :
    long_description = fh . read ()

setuptools . setup (
    name = "simpot" ,
    version = "0.0.1" ,
    author = "Sergio Souza Costa" ,
    author_email = "prof.sergio.costa@gmail.com" ,
    description = "A simple Python object-triple mapping. ...." ,
    long_description = long_description ,
    long_description_content_type = "text/markdown" ,
    url = "https://github.com/inovacampus/simpot" ,
    packages = setuptools . find_packages (),
    install_requires=[
          'rdflib',
    ],
    classifiers = [
        "Programming Language :: Python :: 3" ,
        "License :: OSI Approved :: MIT License" ,
        "Operating System :: OS Independent" ,
    ],
)