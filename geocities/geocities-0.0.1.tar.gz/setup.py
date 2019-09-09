import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geocities",
    version="0.0.1",
    author="Vladimir Udartsev",
    author_email="v.udartsev@gmail.com",
    description="Search Cities and Countries by name, address, lat/long point or geonames_id. Returns polygons geojson.",
    url="https://github.com/udartsev/geocities.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
       'geopy',
       'json',
       'urllib3',
       'transliterate',
       'langdetect',
    ]
)
