from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

# Get the long description from the README file
README = (HERE / "README.md").read_text()

setup(
    name='smockrawl',  # Required
    version='0.1.2',  # Required
    description='Smockeo API crawler',  # Optional
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/fedus/smockrawl',  # Optional
    author='Federico Gentile',  # Optional
    author_email='misc+smockrawl@dillendapp.eu',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        "console_scripts": [
            "smockeo=smockrawl.__main__:main",
        ]
    },
    keywords='smockeo cobject smoke fire detector api crawl crawler',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    python_requires='>=3.5',
    install_requires=['beautifulsoup4', 'python-dateutil', 'humanfriendly', 'requests'],  # Optional

)