from setuptools import setup


setup(
    name='flask-carbon-statsd',
    version='0.0.1',
    url='https://github.com/labeneator/flask_carbon_statsd.git',
    license='BSD',
    author='lmwangi',
    author_email='l.mwangi@gmail.com',
    description='Flask metrics in Carbon Statsd format.',
    long_description=__doc__,
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
