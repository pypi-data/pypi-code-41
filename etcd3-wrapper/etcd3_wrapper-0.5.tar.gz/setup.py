import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
   name='etcd3_wrapper',
   version='0.5',
   description='A wrapper around etcd3 package',
   long_description=long_description,
   long_description_content_type='text/markdown',
   url='https://code.ungleich.ch/ungleich-public/etcd3_wrapper',
   author='ungleich',
   author_email='hacking@ungleich.ch',
   packages=setuptools.find_packages(),
   install_requires=[
          'etcd3',
   ],
   classifiers=[
        'Programming Language :: Python :: 3',
   ],
   python_requires='>=3.6',
)
