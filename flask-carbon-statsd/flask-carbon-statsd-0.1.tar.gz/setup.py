from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='flask-carbon-statsd',
    version='0.1',
    url='https://github.com/labeneator/flask_carbon_statsd.git',
    license='BSD',
    author='lmwangi',
    author_email='lmwangi@gmail.com',
    description='Flask metrics in Carbon Statsd format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['flask_carbon_statsd'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    iqnstall_requires=[
        'Flask',
        'statsd',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
