import setuptools

with open("README.MD",'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='crawlerHelper',
    version='0.0.1',
    author='Wyatt Huang',
    author_email='p@hty.email',
    description='tools which can easy the process of making crawler',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/snippets/1873717',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)