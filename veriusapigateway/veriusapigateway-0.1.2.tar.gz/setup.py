import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="veriusapigateway",
    version="0.1.2",
    author="İlke Elvan",
    author_email="ilke.elvan@verius.com.tr",
    description="API Gateway for accessing Verius Web Services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/veriusai/veriusapigateway/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
