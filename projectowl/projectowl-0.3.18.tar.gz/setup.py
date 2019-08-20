from setuptools import setup, find_packages, find_namespace_packages

# only used for dev.
requirements = []
test_requirements = []
try:
  from pipenv.project import Project
  from pipenv.utils import convert_deps_to_pip
  pfile = Project(chdir=False).parsed_pipfile
  requirements = convert_deps_to_pip(pfile['packages'], r=False)
  # remove local dep.
  requirements = [r for r in requirements if "-e" not in r]
  print("normal requirements: {}".format(requirements))
  test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)
  # remove local dep.
  test_requirements = [r for r in test_requirements if "-e" not in r]
  print("dev requirements: {}".format(test_requirements))
except Exception as ex:
  print("fail to get pipenv dependencies: {}".format(str(ex)))

setup(name="projectowl",
      version="0.3.18",
      description="Utility library for building python app",
      url="https://github.com/flyfj/projectowl.git",
      author="Jie Feng",
      author_email="jiefeng@perceptance.io",
      package_dir={"": "src"},
      packages=find_namespace_packages(where="src"),
      install_requires=requirements,
      tests_require=test_requirements,
      include_package_data=True,
      zip_safe=False)
