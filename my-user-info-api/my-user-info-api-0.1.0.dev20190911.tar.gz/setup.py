from setuptools import setup, find_packages

setup(
    name='my-user-info-api',
    version='0.1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask==1.1.1', 
        'flask-sqlalchemy==2.4.0', 
        'psycopg2==2.8.3',
        'flask-migrate==2.5.2',
        'Flask-API==1.1',
        'flask-script==2.0.6',
        'pytest==5.1.1'
    ]
)