import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Cloud_Kafka_Logger",
    version="0.1.7",
    author="Ganesh",
    author_email="ganeshmoorthy.va@gmail.com",
    description="Send Message To Cloud Kafka Topic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/ganiboy/cloud-kafka-logger",
    # packages=setuptools.find_packages(),
    py_modules=['cloudKafkaLogger'],
    install_requires=[
          'confluent_kafka',
      ],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
