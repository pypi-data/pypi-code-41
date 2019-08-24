from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='sdkBraspag',
    version='0.0.3',
    author='Diego Faria',
    author_email='diego.rdfaria@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
    description='Projeto de SDK para o Split de Pagamentos',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='',
    license='MIT',
    keywords='SDK Braspag Split',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]

)