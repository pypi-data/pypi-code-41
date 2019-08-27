import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name="aime_detector_sdk", version="0.0.5", author="TrinhQuan", author_email="quantv@aimesoft.com",
                 description="Base module for human detection", long_description=long_description,
                 url='https://github.com/jarklee/aime_detector_sdk',
                 download_url='https://github.com/jarklee/aime_detector_sdk/releases/download/0.0.3/aime_detector_sdk-0.0.4.tar.gz',
                 long_description_content_type="text/plain", packages=setuptools.find_packages(),
                 install_requires=['opencv-python==4.1.0.25'],
                 classifiers=["Programming Language :: Python :: 3.6", "Programming Language :: Python :: 3.7",
                              "License :: OSI Approved :: MIT License"], )
