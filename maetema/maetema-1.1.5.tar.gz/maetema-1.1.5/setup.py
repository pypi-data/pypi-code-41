from setuptools import setup, find_packages

VERSION = '1.1.5'


setup(
    name="maetema",
    version=VERSION,
    url='https://docs.maeorg.site',
    license='MIT',
    description='Tema de MaeDocs',
    author='Ham Won Trikru',
    author_email='lwonderlich@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'maeguias.themes': [
            'mae = mae',
        ]
    },
    zip_safe=False
)
