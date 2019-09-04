from setuptools import setup

from todo.todo import VERSION


def readme():
    with open('README.md') as file_pointer:
        return file_pointer.read()


setup(
    name='FNE-todo',
    version=VERSION,
    description='Simple command-line Todo app.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: General',
    ],
    keywords='todo task',
    url='https://github.com/FatmanurEraslan/Todo1',
    author='Fatmanur Eraslan',
    author_email='fatmanur13.fe@gmail.com',
    license='MIT',
    packages=['todo'],
    entry_points={'console_scripts': ['todo=todo.commandline:main']},
    include_package_data=True,
    zip_safe=False,
)
