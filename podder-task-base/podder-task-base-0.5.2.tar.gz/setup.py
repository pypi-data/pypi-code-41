from setuptools import setup, find_packages

from podder_task_base import __version__ as version

with open('requirements.txt') as file:
    install_requires = file.read()

setup(
    name='podder-task-base',
    version=version,
    packages=find_packages(),
    author="podder-ai",
    url='https://github.com/podder-ai/podder-task-base',
    include_package_data=True,
    install_requires=install_requires,
    package_data = {
        'podder_task_base': [
            'task_initializer/templates/*',
            'task_initializer/templates/api/*',
            'task_initializer/templates/api/protos/*',
            'task_initializer/templates/scripts/*',
        ],
    },
)
