from setuptools import setup
# TODO: Fix the fact that lib files aren't transferring at all, just __init__.py and command_line.py
def readme():
      with open('README.md') as f:
            return f.read()

setup(name='squp',
      version='0.1.8',
      description='A backend engine for Squarespace that uses splinter/selenium for automated data entry',
      long_description=readme(),
      classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.7',
            'Intended Audience :: End Users/Desktop',
            'Environment :: Win32 (MS Windows)',
            'Intended Audience :: Customer Service',
            'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
            'Topic :: Software Development :: User Interfaces',
            'Topic :: Internet :: WWW/HTTP :: Browsers',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Internet :: WWW/HTTP :: Session',
            'Topic :: Internet :: WWW/HTTP :: Site Management',
            'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking'
      ],
      keywords='ecommerce automation web splinter selenium squarespace',
      url='https://github.com/Ninjaura314/squp',
      author='Jonathan Hoyle',
      author_email='jonathanhoyle314@gmail.com',
      license='Mozilla Public License 2.0 (MPL 2.0)',
      packages=['squp'],
      install_requires=[
            'addict',
            'ahk',
            'appJar',
            'arrow',
            'beautifulsoup4',
            'bottle',
            'colour',
            'dataset',
            'docker',
            'dominate',
            'ftfy',
            'lxml',
            'pillow',
            'pyautogui',
            'pypiwin32',
            'pywebview',
            'pywin32',
            'scrapy',
            'selenium',
            'splinter',
            'urllib3',
      ],
      include_package_data=True,
      entry_points={
          'console_scripts': ['squp=squp.command_line:main'],
      },
      zip_safe=False)