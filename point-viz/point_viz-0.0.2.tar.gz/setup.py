import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="point_viz",
    version="0.0.2",
    author="Zhaoyu Su",
    author_email="zsuad@connect.ust.hk",
    description="A light-weight web point cloud visualizer based on Three.js",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SUZhaoyu/point_viz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)