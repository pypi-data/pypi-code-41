import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'nameko_django_gateway_utils',
    version = '0.0.5',
    author = 'li1234yun',
    author_email = 'li1234yun@163.com',
    description = 'nameko django as gateway utils',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/li1234yun/nameko-django-gateway-utils',
    packages = setuptools.find_packages(),
    install_requires = [
        'nameko'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
