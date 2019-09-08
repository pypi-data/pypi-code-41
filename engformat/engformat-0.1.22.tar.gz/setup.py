from setuptools import setup

about = {}
with open("engformat/__about__.py") as fp:
    exec(fp.read(), about)

setup(name='engformat',
      version=about['__version__'],
      description='Tools for displaying engineering calculations according to the Engineering Standard Format',
      url='',
      author='Maxim Millen',
      author_email='millen@fe.up.pt',
      license='MIT',
      packages=[
        'engformat',
    ],
    install_requires=[
        "numpy",
        "bwplot>=0.2.10",
        "sfsimodels",
        "matplotlib",
        "eqsig"
    ],
      zip_safe=False)