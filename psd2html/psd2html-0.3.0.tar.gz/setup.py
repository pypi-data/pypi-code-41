from setuptools import setup

# This call to setup() does all the work
setup(
    name="psd2html",
    version="0.3.0",
    description="Convert PSD file to HTML",
    long_description=(
      open('README.md').read()
    ),
    url="https://github.com/kimngei/psd2html",
    author="Andrew Ngei",
    author_email="andrew@kimngei.pro",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[
        "psd2html"
    ],
    include_package_data=True,
    python_requires='>=3',
    install_requires=[
        "psd-tools",
        "lxml",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "psd2html=psd2html.__main__:main",
        ]
    },
)
