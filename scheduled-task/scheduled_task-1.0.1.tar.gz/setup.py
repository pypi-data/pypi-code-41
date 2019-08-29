import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='scheduled_task',
    version='1.0.1',
    author='Artem Kryvonis',
    license='MIT',
    author_email='me@kryvonis.com',
    description='scheduled tasks for Python 3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Kryvonis/scheduled_task',
    packages=['scheduled_task'],
    classifiers=[
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)