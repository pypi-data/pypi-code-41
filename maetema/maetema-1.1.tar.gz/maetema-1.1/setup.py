from setuptools import setup, find_packages

VERSION = '1.1'

with open("requirements.txt") as data:
    install_requires = [
        line for line in data.read().split("\n")
            if line and not line.startswith("#")
    ]

setup(
    name="maetema",
    version=VERSION,
    url='https://docs.maeorg.site',
    license='MIT',
    description='Mae Tema',
    author='Ham Won Trikru',
    author_email='lwonderlich@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires = install_requires,
    entry_points={
        'maeguias.themes': [
            'maetema = maetema',
        ]
    },
    zip_safe=False
)
