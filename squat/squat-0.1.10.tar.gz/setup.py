import setuptools


try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [
        "{} @ {}".format(
            str(ir.req),
            'https://artifactory.global.standardchartered.com/artifactory/api/pypi/pypi/simple')
        for ir in reqs
    ]


setuptools.setup(
     name='squat',
     version='0.1.10',
     scripts=[] ,
     author="Binay Kumar Ray",
     author_email="binaykumar.ray@sc.com",
     description="bankstatement analyser",
     long_description='bs analyser',
     long_description_content_type="text/markdown",
     url="https://bitbucket.global.standardchartered.com/scm/~1586202/squat.git",
     packages=setuptools.find_packages(),
     include_package_data=True,
     # install_requires=load_requirements('requirements.txt'),
     # dependency_links=[
     #     'https://artifactory.global.standardchartered.com/artifactory/api/pypi/pypi/simple'
     #  ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )