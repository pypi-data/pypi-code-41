from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='SGfunniest',
      version='0.1.9',
      description='The funniest joke in the world',
      long_description='Really, the funniest around.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='funniest joke comedy flying circus',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['SGfunniest'],
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)