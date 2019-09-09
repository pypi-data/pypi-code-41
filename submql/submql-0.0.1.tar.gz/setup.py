from setuptools import find_packages, setup

setup(
    name='submql',
    packages=find_packages(),
    version='0.0.1',
    author="Quinten Lootens",
    author_email="quinten.lootens@ugent.be",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['gym', 'matplotlib', 'pybullet'],
    python_requires='>=3.6'
)
