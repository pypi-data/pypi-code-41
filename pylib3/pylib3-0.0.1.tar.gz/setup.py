from setuptools import setup
import pylib3

package_name = 'pylib3'
setup(
    name=package_name,
    version=pylib3.get_version(
        caller=__file__,
        version_file='{}_VERSION'.format(package_name.upper())
    ),
    include_package_data=True,
    packages=[package_name],
    install_requires=[
        'termcolor==1.1.0'
    ],
    scripts=[],
    url='',
    license='MIT License',
    author='Shlomi Ben-David',
    author_email='shlomi.ben.david@gmail.com',
    description='Python Shared Library'
)
