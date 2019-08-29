from setuptools import setup, find_packages

install_requires = [
    'docker',
    'appdirs',
]

setup(
    name='ancypwn-backend-windows_remote',
    version='0.0.2',
    description='ancypwn windows remote backend',
    url='https://github.com/Escapingbug/ancypwn-backend-windows_remote',
    author='Anciety',
    author_email='anciety@pku.edu.cn',
    packages=['ancypwn_backend_windows_remote'],
    package_dir={'ancypwn_backend_windows_remote': 'src'},
    install_requires=install_requires
)
