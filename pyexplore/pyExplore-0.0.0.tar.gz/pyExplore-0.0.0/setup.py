import setuptools
import pathlib

HERE = pathlib.Path(__file__).parent


setuptools.setup(name='pyExplore',
                 version='0.0.0',
                 description='Python Package for exploratory data analysis in Data Science',
                 long_description=open('README.md').read().strip(),
                 long_description_content_type = 'text/markdown',
                 author='Rahul Mishra',
                 author_email='rahul.mishra2003@gmail.com',
                 url='https://github.com/rahul1809/pyExplore',
                 py_modules=['pyExplore'],
                 install_requires=['pandas', 'matplotlib', 'numpy', 'scipy'],
                 license='MIT License',
                 zip_safe=False,
                 keywords='Exploratory Data Analysis, Data Analysis,EDA',
                 classifiers=["License :: OSI Approved :: MIT License",
                              "Programming Language :: Python :: 3",
                              "Programming Language :: Python :: 3.7"
                              ])
