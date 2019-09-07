import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="turta_relayhat2",
    version="1.0.1",
    author="Turta LLC",
    author_email="hello@turta.io",
    description="Python Libraries for Turta Relay HAT 2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.turta.io/relayhat",
    packages=setuptools.find_packages(),
    install_requires=["smbus"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Topic :: System :: Hardware",
    ],
    project_urls={
        'Documentation': 'https://docs.turta.io/raspberry-pi-hats/relay-hat-2',
        'Community': 'https://community.turta.io',
        'GitHub Repository' : 'https://github.com/Turta-io/RelayHAT2',
    },
)