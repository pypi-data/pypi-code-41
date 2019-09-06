import setuptools

with open('requirements.txt', 'r') as file:
    requirements = file.read().splitlines(keepends = False)

with open('README.rst', 'r') as file:
    README = file.read()

setuptools.setup(
    name='slackspread',
    version='0.0.1',
    description="Wrappers around gspread and slack API",
    long_description=README,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    include_package_data=True,
    author='Romain Damian',
    author_email='damian.romain@gmail.com'
)
