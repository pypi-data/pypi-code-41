import subprocess
import os.path as osp
import os

CONDA_BUILD_DIR = osp.join(osp.dirname(osp.abspath(__file__)), 'conda_builds')
PACKAGE_NAME = 'pydicom-1.0.2-py36_0.tar.bz2'
PY_VERSIONS = ('34', '35', '36')


def build():
    for version in PY_VERSIONS:
        subprocess.run('conda build --python={}'.format(version), cwd=CONDA_BUILD_DIR)


def convert():
    for version in PY_VERSIONS:
        subprocess.run('conda convert --platform all -f win-64/pydicom-1.0.2-py{}_0.tar.bz2'.format(version),
                       cwd=CONDA_BUILD_DIR)


def upload():
    for platform in ('linux-32', 'linux-64', 'osx-64', 'win-32', 'win-64', 'linux-armv7l'):
        subprocess.run('anaconda upload {}/pydicom-1.*'.format(platform), cwd=CONDA_BUILD_DIR)
