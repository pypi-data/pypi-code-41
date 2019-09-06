from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

    setup(name='pymalscraper',
          version='1.0.2',
          author='prinsepipo',
          author_email='prinse.sanchez@gmail.com',
          description='Simple Anime Web Scraper.',
          long_description=long_description,
          long_description_content_type="text/markdown",
          url='https://github.com/prinsepipo/anime-scraper',
          license='MIT',
          packages=find_packages(),
          zip_safe=False)
