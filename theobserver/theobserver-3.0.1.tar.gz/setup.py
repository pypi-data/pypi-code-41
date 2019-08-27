from setuptools import setup


setup(
    name='theobserver',
    packages=['theobserver'],
    version='3.0.1',
    description='A dataset characteristic extractor for machine learning processing.',
    author='Bernardo Trevizan',
    author_email='trevizanbernardo@gmail.com',
    url='https://github.com/btrevizan/theobserver',
    keywords='feature,characteristic extraction,machine learning',
    install_requires=['pandas', 'scikit-learn']
)
