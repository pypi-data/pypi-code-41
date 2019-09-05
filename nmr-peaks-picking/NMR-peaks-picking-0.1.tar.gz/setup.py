import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='NMR-peaks-picking',
    version='0.1',
    packages=['NMR'],
    description='',
    long_description=README,
    author='Chinya Chao',
    author_email='C.Chao@liverpool.ac.uk',
    url='https://github.com/ChinyaChao/NMR-peaks-picking-website',
    license='MIT',
    install_requires=[
        'Django==2.2.5',
        'django-cleanup==4.0.0',
        'imageio==2.5.0',
        'matplotlib==3.1.1',
        'nmrglue==0.7',
        'numpy==1.17.1',
        'Pillow==6.1.0',
        'scikit-image==0.15.0',
        'scikit-learn==0.21.3',
        'scipy==1.3.1'
    ]
)