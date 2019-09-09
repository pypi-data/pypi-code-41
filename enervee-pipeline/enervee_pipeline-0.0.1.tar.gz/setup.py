from setuptools import setup, find_packages


setup(name='enervee_pipeline',
      version='0.0.1',
      description='Handles sending, receiving and saving data through queues and cloud storage',
      url='https://gitlab.enervee.com/enervee/enervee_pipeline',
      author='David Newcomb',
      author_email='david.newcomb@enervee.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
