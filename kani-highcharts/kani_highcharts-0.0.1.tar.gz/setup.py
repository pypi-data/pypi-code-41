import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

ns = {}
with open(os.path.join(here, 'kani_highcharts', 'version.py')) as f:
    exec(f.read(), {}, ns)

setup(
    name='kani_highcharts',
    version=ns['__version__'],
    author='fx-kirin',
    author_email='fx-kirin@gmail.com',
    packages=find_packages(),
    package_data={
        'kani_highcharts.highcharts': ['templates/*.html'],
        'kani_highcharts.highmaps': ['templates/*.html'],
        'kani_highcharts.highstock': ['templates/*.html']
    },
    url='https://github.com/fx-kirin/kani_highcharts',
    description='Python Highcharts wrapper',
    install_requires=[
        "Jinja2",
        "future"
    ],
    keywords=['python', 'ipython', 'highcharts', 'chart', 'visualization', 'graph', 'javascript', 'html'],
    classifiers=[
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
