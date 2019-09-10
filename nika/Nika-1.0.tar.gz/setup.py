import setuptools

print(setuptools.find_packages())

with open("README.md", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="Nika",
    version="1.0",
    author="Bekkazy Kubanychbekov",
    author_email="bekkazy.k@gmail.com",
    description="Package for process data from some source",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bekkazy-k/Nika",
    packages=setuptools.find_packages(),
    install_requires=[
        'kafka-python==1.4.6',
        'profig==0.4.1',
        'psycopg2==2.8.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
