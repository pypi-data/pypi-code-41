import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Workerpy",
    version="1.1.0",
    author="Enoi Barrera Guzman",
    author_email="zafiro3000x@gmail.com",
    description="Libreria para crear Workers que responden a eventos desde kafka/Nats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        'kafka-python==1.4.6',
        'Logbook==1.4.3',
        'asyncio-nats-client==0.9.2',
        'python-dotenv==0.10.3'
    ]
)