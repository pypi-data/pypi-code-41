import setuptools

with open("README.md", "r") as fh:
      long_description = fh.read()

setuptools.setup(
      name='fixalign',
      version='0.1.0',
      author='Zhen Liu',
      author_email='liuzhen2018@sibs.ac.cn',
      description='find and fix missed small exons',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/zhenLiuExplr/fixalign-project',
      packages=setuptools.find_packages(),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
      ],
)
