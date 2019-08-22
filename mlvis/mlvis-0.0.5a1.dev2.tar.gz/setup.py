from setuptools import setup, find_packages
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install
import os, subprocess


INSTALL_REQUIRES = [
    'traitlets',
    'ipywidgets'
]


extension_dir = os.path.join(os.path.dirname(__file__), "mlvis", "static")


here = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    return open(os.path.join(here, *parts), 'r').read()


class develop(_develop):
    def run(self):
        from notebook.nbextensions import install_nbextension
        from notebook.services.config import ConfigManager

        _develop.run(self)

        install_nbextension(extension_dir, symlink=True,
                            overwrite=True, user=False, destination="mlvis")
        cm = ConfigManager()
        cm.update('notebook', {"load_extensions":
            {
                "mlvis/index": True,
                "mlvis/extension": True
            }
        })


class install(_install):
    def run(self):
        subprocess.check_call(['pip', 'install', 'notebook'])

        from notebook.nbextensions import install_nbextension
        from notebook.services.config import ConfigManager

        _install.run(self)

        # A hack for installing the install_requires as there seems to be
        # a issue with custom install command:
        # https://github.com/pypa/setuptools/issues/456
        subprocess.check_call(['pip', 'install'] + INSTALL_REQUIRES)

        install_nbextension(extension_dir, symlink=True,
                            overwrite=False, user=False, destination="mlvis")
        cm = ConfigManager()
        cm.update('notebook', {"load_extensions":
            {
                "mlvis/index": True,
                "mlvis/extension": True
            }
        })


setup(name='mlvis',
      cmdclass={'develop': develop, 'install': install},
      version='0.0.5a1.dev2',
      description='A wrapper around react components for use in jupyter notebooks',
      long_description='{}'.format(read('README.md')),
      long_description_content_type='text/markdown',
      keywords=['data', 'visualization', 'machine learning'],
      url='https://github.com/',
      author='Hong Wang',
      author_email='hongw@uber.com',
      license='MIT',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      data_files=[
        ('share/jupyter/nbextensions/mlvis', [
            'mlvis/static/extension.js',
            'mlvis/static/index.js'
        ]),
      ],
      install_requires=INSTALL_REQUIRES,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Jupyter'
        ]
      )
