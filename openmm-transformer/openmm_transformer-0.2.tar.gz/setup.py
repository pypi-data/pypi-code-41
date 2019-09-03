from setuptools import setup, find_packages

print(find_packages('.'))

setup(name='openmm_transformer',
      version='0.2',
      description='Cleaner way to manage custom forces in openmm',
      url='http://github.com/mohebifar/openmm-transformer',
      author='Mohamad Mohebifar',
      author_email='mmohebifar@mun.ca',
      license='MIT',
      packages=['openmm_transformer', 'openmm_transformer.utilities',
                'openmm_transformer.transformers', 'openmm_transformer.expressions'],
      include_package_data=True,
      zip_safe=False,
      package_data={'openmm_transformer': ['expressions/*']}
      )
