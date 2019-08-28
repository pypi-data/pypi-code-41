from setuptools import setup 
  
# reading long description from file 
with open('DESCRIPTION.txt') as file: 
    long_description = file.read() 
  
  
# specify requirements of your package here 
REQUIREMENTS = ['requests'] 
  
# some more details 
CLASSIFIERS = [ 
    'Development Status :: 4 - Beta', 
    'Intended Audience :: Developers', 
    'Topic :: Internet', 
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python', 
    'Programming Language :: Python :: 2', 
    'Programming Language :: Python :: 2.6', 
    'Programming Language :: Python :: 2.7', 
    'Programming Language :: Python :: 3', 
    'Programming Language :: Python :: 3.3', 
    'Programming Language :: Python :: 3.4', 
    'Programming Language :: Python :: 3.5', 
    ] 
  
# calling the setup function  
setup(name='CPSReleaseTool', 
      version='1.0.0', 
      description='A tool to fetch data from urls to a pdf or a word file.', 
      long_description=long_description, 
      url='https://github.com/Vishakha34/CPSReleaseTool', 
      author='Vishakha Verma', 
      author_email='vishakhaverma8657@gmail.com', 
      license='MIT', 
      packages=['CPSReleaseTool'], 
      classifiers=CLASSIFIERS, 
      install_requires=REQUIREMENTS, 
      keywords='python url parsing urlparsing cpsreleasetool cps pdf word'
      ) 
