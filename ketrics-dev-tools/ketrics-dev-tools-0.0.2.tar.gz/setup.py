from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

meta = {}
with open('./src/ketrics_dev_tools/version.py') as f:
    exec(f.read(), meta)

setup(
    name="ketrics-dev-tools",
    version=meta['__version__'],
    author="Cristian Bustamante",
    author_email="cristian@ketrics.com",
    description="This package is for Ketrics Application Developers",
    keywords="ketrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.ketrics.com",
    project_urls={
        "Documentation": "https://github.com/ketrics/ketrics-dev-tools",
        "Source Code": "https://github.com/ketrics/ketrics-dev-tools",
    },
    packages=find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['python-dotenv>=0.10.3', 'requests>=2.22.0'],
    package_dir={
        '': 'src',
    },
    entry_points={
        'console_scripts': ['ketrics-dev-tools=ketrics_dev_tools.command_line:main'],
    },
)