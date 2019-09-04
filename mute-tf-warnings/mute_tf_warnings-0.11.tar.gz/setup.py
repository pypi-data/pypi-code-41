import setuptools
import os

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setuptools.setup(name='mute_tf_warnings',
      version='0.11',
      description='a package for allocating tensorflow gpu memory use in python',
      url='https://github.com/kongkip/mute_tf_warnings',
      long_description=str(README),
      long_description_content_type="text/markdown",
      author='Evans Kiplagat',
      author_email='evanskiplagat3@gmail.com',
      license='MIT',
      packages=setuptools.find_packages(),
      zip_safe=False)
