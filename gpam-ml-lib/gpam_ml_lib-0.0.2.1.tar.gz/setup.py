import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gpam_ml_lib",
    version="0.0.2.1",
    author="Victor Coelho, Guilherme Aguiar",
    author_email="victorhdcoelho@gmail.com, gui9627oli@gmail.com",
    description="Machine Learn library for kaggle problems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gpam/teesw/2019_2/gpam-ml-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "keras", "numpy", "pandas", "Pillow", "scikit-learn", "scipy",
        "seaborn", "tensorflow", "tqdm", "scikit-image", "opencv-python"
    ],
)
