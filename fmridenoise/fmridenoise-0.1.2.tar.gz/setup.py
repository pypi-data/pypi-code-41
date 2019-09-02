import setuptools
from os.path import join, dirname, relpath
import glob
from fmridenoise.pipelines import get_pipelines_paths
from fmridenoise.parcellation import get_parcelation_file_path, get_distance_matrix_file_path
from fmridenoise.utils.templates import get_all_templates
from itertools import chain
with open("README.md", "r") as fh:
    long_description = fh.read()

def get_requirements() -> list:
    with open(join(dirname(__file__), 'requirements.txt'), 'r') as req:
        output = [str(line) for line in req]
        return output

def relative_paths(paths: list) -> list:
    return [ relpath(path, join(dirname(__file__), 'fmridenoise')) for path in paths ]

parcelation_path = [get_parcelation_file_path(), get_distance_matrix_file_path()]
test = list(chain(relative_paths(get_pipelines_paths()), 
                                            relative_paths(parcelation_path),
                                            relative_paths(get_all_templates())))
setuptools.setup(
    name="fmridenoise",
    version="0.1.2",
    author="Karolina Finc, Mateusz Chojnowski, Kamil Bona",
    author_email="karolinafinc@gmail.com, zygfrydwagner@gmail.com, kongokou@gmail.com",
    description="fMRIDenoise - automated denoising, denoising strategies comparison, and functional connectivity data quality control.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nbraingroup/fmridenoise",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*tests*"]),
    install_requires=get_requirements(),
    package_data={'fmridenoise': list(chain(relative_paths(get_pipelines_paths()), 
                                            relative_paths(parcelation_path),
                                            relative_paths(get_all_templates())))},
    scripts=['fmridenoise/scripts/fmridenoise']
)
