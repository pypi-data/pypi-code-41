import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='seakyez',
    version='1.0.5',
    author='Seaky Lone',
    author_email='luokiss9@qq.com',
    description='An package that makes Python programming easy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SeakyLuo/PythonFiles',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]    
)
