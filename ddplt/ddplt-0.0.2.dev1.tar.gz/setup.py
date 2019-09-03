import ddplt
import setuptools

setuptools.setup(name="ddplt",
                 version=ddplt.__version__,
                 packages=["ddplt"],
                 install_requires=['matplotlib>=3.1'
                                   'scikit-learn>=0.21',
                                   'numpy>=1.16',
                                   'pandas>=0.23'],

                 author="Daniel Danis",
                 author_email="daniel.gordon.danis@gmail.com",
                 url="https://github.com/ielis/ddplt",
                 description="Useful utility functions for evaluation of ML",
                 license='GPLv3',
                 keywords="plotting machine learning evaluation metrics",
                 test_suite='tests')
