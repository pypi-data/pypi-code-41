from distutils.core import setup
from airflow_xplenty.version import VERSION


def do_setup():
    setup(
      name='airflow_xplenty',
      packages=['airflow_xplenty', 'airflow_xplenty.operators'],
      version=VERSION,
      description='Airflow wrappers for the Xplenty API',
      author='Tom Collier',
      author_email='collier@apartmentlist.com',
      url='https://github.com/apartmentlist/airflow_xplenty',
      download_url=(
        'https://github.com/apartmentlist/airflow_xplenty/archive/' + VERSION +
        '.tar.gz'),
      keywords=['airflow', 'xplenty'],
      install_requires=['apache-airflow (== 1.9.0)', 'xplenty (>= 1.2.0)'],
      classifiers=['Programming Language :: Python :: 3']
    )


if __name__ == "__main__":
    do_setup()
