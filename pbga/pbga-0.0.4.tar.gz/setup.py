import pbga
import io
import setuptools

setuptools.setup(name='pbga',
                 version=pbga.__version__,
                 packages=['pbga'],
                 install_requires=['psycopg2-binary>=2.8.3'],

                 long_description=io.open('README.md', encoding='utf-8').read(),
                 long_description_content_type='text/markdown',

                 author='Daniel Danis',
                 author_email='daniel.gordon.danis@gmail.com',
                 url='https://github.com/TheJacksonLaboratory/PBGA-python-toolkit',
                 description='Library of Python utilities for PacBio Genomes Analysis',
                 license='GPLv3',
                 keywords='bioinformatics genomics',

                 package_data={'pbga': ['jar/h2-1.4.199.jar']},
                 test_suite='tests')
