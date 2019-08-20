import setuptools

with open('requirements.txt', 'r') as file:
    requirements = file.read().splitlines(keepends = False)

with open('README.rst', 'r') as file:
    README = file.read()

setuptools.setup(
    name='pyux-track',
    version='0.1.2',
    description="Python ux tools to ease tracking scripts",
    long_description=README,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    include_package_data=True,
    author='Romain Damian',
    author_email='damian.romain@gmail.com',
    url='https://pyux.readthedocs.io/en/stable/'
)
