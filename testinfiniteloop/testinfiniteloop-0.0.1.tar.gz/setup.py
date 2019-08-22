import setuptools
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        print("never ends")
        while True: pass
        print("Installing done!")

setuptools.setup(
    name="testinfiniteloop",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    packages=setuptools.find_packages(),
    cmdclass={
        'install': CustomInstallCommand,
    },
)
