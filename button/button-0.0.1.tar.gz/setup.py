from setuptools import setup, find_packages

setup(
    name='button',
    version='0.0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},

    python_requires='>=3.*',

    author='Minhwan Kim',
    author_email='minhwan.kim@member.fsf.org',
    description='Tiny automation tool written by Python',
    keywords='automation build tool',
    url='https://github.com/somssi/button',
    project_urls={
        'Documentation': 'https://github.com/somssi/button',
        'Source Code': 'https://github.com/somssi/button',
    },
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],

    entry_points={
        'console_scripts': [
            'btn = button.cli:main',
        ],
    },
)
