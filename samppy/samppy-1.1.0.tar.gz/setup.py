import setuptools
import samppy

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="samppy",
    version=samppy.__version__,
    author="Arne Leijon",
    author_email="leijon@kth.se",
    description="Hamiltonian sampling and analysis of sampled distributions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ),
    keywords = 'sampling Hamiltonian MCMC Bayesian credibility entropy',
    install_requires=['numpy>=1.17', 'scipy'],
    python_requires='>=3.6',
    py_modules=['hamiltonian_sampler', 'credibility']
)
