import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='EpisodeFixer',  
     version='1.0.5',
     packages=['EpisodeFixer'] ,
     entry_points={'console_scripts': ['EpisodeFixer = EpisodeFixer.EpisodeFixer:main']},
     author="Vasu Jain",
     author_email="jain.vasu.631@gmail.com",
     description="An Episode Fixer which can embed subtitles and rename episodes.",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/jainvasu631/EpisodeFixer",
     download_url="https://github.com/jainvasu631/EpisodeFixer/archive/v1.0.5.tar.gz",
     install_requires=['bs4'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
         "Natural Language :: English",
     ],
 )