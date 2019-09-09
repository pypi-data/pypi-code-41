from distutils.core import setup
setup(
    name='Probationem',
    packages=['Probationem'],
    version='1.0.4',
    license='MIT',
    description='Generator fuer Ausbildungsnachweise (Fachinformatiker)',
    author='Julius Dehner',
    author_email='julius.dehner@gmail.com',
    url='https://github.com/juligreen/Probationem',
    download_url='https://github.com/juligreen/Probationem/archive/1.0.4.tar.gz',
    keywords=['generator', 'certificate', 'automation'],
    install_requires=[
        'fpdf',
        'toml',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        "console_scripts": [
            "probationem=Probationem.main:probationem",
        ]
    },
)
