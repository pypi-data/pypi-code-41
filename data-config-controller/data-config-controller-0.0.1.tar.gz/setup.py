import setuptools

with open('README.md', 'r') as read_me:
    description = read_me.read()

setuptools.setup(
    name='data-config-controller',
    version='0.0.1',
    author='James Beringer',
    author_email='jamberin@gmail.com',
    description='Database adn config controller ',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/jamberin/data_config_controller',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3'
    ]
)