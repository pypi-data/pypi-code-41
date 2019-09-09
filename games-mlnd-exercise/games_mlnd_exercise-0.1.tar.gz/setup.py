# TODO: Fill out this file with information about your package

# HINT: Go back to the object-oriented programming lesson "Putting Code on PyPi" and "Exercise: Upload to PyPi"

# HINT: Here is an example of a setup.py file
# https://packaging.python.org/tutorials/packaging-projects/

from setuptools import setup

setup(name='games_mlnd_exercise',
      version='0.1',
      description='A package containing list of games to play',
      packages=['games'],
      zip_safe=False)
