# -*- coding: utf-8 -*-
"""This file will create an instance of a new project with default settings"""
import os
import shutil
from datetime import datetime
import errno
from backports import configparser2
from jinja2 import Environment, PackageLoader, select_autoescape
from py_guide import log_4_trees as logging


class PyProject(object):
    def __init__(self, logger=None, project_name="python_project"):
        self._project_name = project_name
        self.log = logger
        self.author = ""

    def create(self):
        """Create a template project on disk from the information in the object    """
        self.create_project_directories(self.project_name)
        self.create_core_files()

    def create_core_files(self):
        """Creates standard files for all projects following this Python guide.  As a pattern this method will call
        another method to create the file.  In that method it will handle the data needed for that file, as well as
        calling another method to write the file."""
        env = Environment(
            loader=PackageLoader('py_guide', 'py_template'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        # The following methods will handle determining template and providing data to it while creating files
        self.create_license(environment=env)
        self.create_requirements(environment=env)
        self.create_gitignore(environment=env)
        self.create_docs_source_conf(environment=env)

    def create_docs_source_conf(self, environment=None):
        """Creates the Sphinx configuration file in the docs_source directory

        Args:
            environment(Jinja2.environment): Context for the template engine Jinja2
        """
        # Data for the Sphinx Conf template
        conf_d = {u'project_name': self.project_name}
        conf_t = environment.get_template('docs_source/conf.py')
        self.write_file('docs_source/conf.py', conf_t, conf_d)

    def create_gitignore(self, environment=None):
        """Creates the GIT Ignore file.  This list excludes things in the project that should not be checked into
        source control.

        Args:
            environment(Jinja2.environment): Context for the template engine Jinja2
        """
        git_t = environment.get_template('.gitignore')
        self.write_file(".gitignore", git_t)

    def create_license(self, environment=None):
        """Creates the LICENSE file for the project.

        Args:
            environment(Jinja2.environment): Context for the template engine Jinja2
        """
        # Data for the license template as a Python dictionary
        license_d = {u'year': u'{0}'.format(str(datetime.now().year)),
                     u'copyright_holder': u'{0}'.format(self.author)}

        license_t = environment.get_template('LICENSE-MIT')

        self.write_file("LICENSE", license_t, license_d)

    def create_project_directories(self, project_name):
        directory = os.path.join(self.find_project_base_directory(), project_name)
        self.make_directory(directory)
        project_name_root = directory
        # documentation html directory; the has been generated end result
        directory = os.path.join(project_name_root, "docs")
        self.make_directory(directory)
        # documentation source directory, for the projects documentation
        directory = os.path.join(project_name_root, "docs_source")
        self.make_directory(directory)
        # documentation source directory, for the code documentation
        directory = os.path.join(project_name_root, "docs_source", "code")
        self.make_directory(directory)
        # source code directory [should reference use same name PEP here]
        directory = os.path.join(project_name_root, project_name)
        self.make_directory(directory)
        # virtual environment
        directory = os.path.join(project_name_root, "venv")
        self.make_directory(directory)

    def create_requirements(self, environment=None):
        """Creates the requirements.txt file.  This file is used by Python to update a projects virtual environment
        with the packages needed to run the project.  Initialized with core packages that are needed for all projects
        like pip, setuptools and wheel, and packages needed to follow good practices like documentation,  such as
        sphinx.

        Args:
            environment(jinja2.Environment): Context for the template engine Jinja2.
                https://jinja.palletsprojects.com/en/2.10.x/api/#jinja2.Environment
        """
        requirements_t = environment.get_template('requirements.txt')
        self.write_file(file_name="requirements.txt", template=requirements_t)

    def find_project_base_directory(self):
        """Determines a directory for creating the new project.  First check to see if there is a PycharmProjects
        directory in use.  If so use it.  If not then just use the user directory."""
        # Do they use PyCharm?
        project_dir = r"{0}\{1}".format(os.path.expanduser("~"), "PycharmProjects")
        if os.path.exists(project_dir):
            self.project_directory = project_dir
        else:
            project_dir = r"{0}".format(os.path.expanduser("~"))
            self.project_directory = project_dir

        # We could also find a path relative to this file
        # directory_file = os.path.dirname(__file__)
        # Relative to this file could be the py_guide root
        # py_guide_root = os.path.join(directory_file, "..")

        return self.project_directory

    def make_directory(self, directory_path=None):
        """Creates a directory for the project.  Handles errors and logging"""
        try:
            os.mkdir(directory_path)
            self.log.info("Created directory {0}".format(directory_path))
        except FileExistsError as e:
            self.log.info("Directory {0} already exists.".format(directory_path))
            raise e
        except OSError as e:
            self.log.error(r"Failed to created directory {0}.\n\rError indicates {1}".format(directory_path,
                                                                                             e.strerror))
            raise e

    def remove_directory(self, project_name):
        """Primarily created for when make_directory experiences a FileExistsError, this method will delete an
        existing project folder.  It takes the name we pass (or wnated to create) and finds it in the project directory
        path.  This allows the calling user interface to not have to understand the full path to the directory."""
        directory = os.path.join(self.find_project_base_directory(), project_name)
        shutil.rmtree(directory)
        self.log.info("Removed directory {0}".format(directory))

    def write_file(self, file_name=None, template=None, template_data={}):
        """Wrapper method for successive file creation.

        Args:
            file_name(str): Name of the file to write
            template(jinja2.Template): The jinja2 template to be written
            template_data(dictionary): Key/Value pairs of data for the jinja2 template
        """
        absolute_file_name = os.path.join(self.project_absolute_path, file_name)
        try:
            with open(absolute_file_name, 'w') as file:
                file.write(template.render(template_data))
                self.log.info("Created file {0}".format(absolute_file_name))
        except EnvironmentError as e:
            self.log.error(e.strerror)

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def project_directory(self):
        return self._project_directory

    @project_directory.setter
    def project_directory(self, value):
        self._project_directory = value

    @property
    def project_absolute_path(self):
        """The abspath() of this file.  The absolute path will be the full file on path on disk for the operating
        system you are on."""
        return os.path.abspath(os.path.join(self.project_directory, self.project_name))

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        if value is None:
            self._log = logging.LoggerOfTrees()
        else:
            self._log = value
