import logging
import os
from menu import menu
from py_guide import project_factory

class ConsoleMenu:
    def __init__(self, cmdline_argument_parser, logger=None):
        self.log = logger
        self.cmdline_parser = cmdline_argument_parser

        self.menu_main = menu.Menu()
        title = """
******************************************
    Python Guide for Practicing Wizards
*******************************************
        """
        self.menu_main.title = title
        self.menu_main.set_options([
                                    ("Generate new project", self.new_project_generator),
                                    ("py_guide help", self.show_help),
                                    ("Exit", self.close_menu)
                                   ])

    def new_project_generator(self):
        """Collects some information, then generates a project using the best practices of this guide."""
        project_name = menu.input("What is the name of your project?")
        py = project_factory.PyProject(project_name=project_name, logger=self.log)
        py.author = menu.input("What name do you want to use for author, copyright holder?")

        try:
            py.create()
        except FileExistsError as e:
            action = menu.input("Directory {0} already exists. (D)elete or (R)ename?".format(py.project_absolute_path))
            if action == "D":
                py.remove_directory(project_name=project_name)
            else:
                new_name = menu.input("What is the new name of your project?")
                project_name = new_name
            py.project_name = project_name
            py.create()

        self.log.info("Your project was created at {0}".format(py.find_project_base_directory()))

    def show_menu(self):
        self.menu_main.open()

    def close_menu(self):
        self.menu_main.close()

    def show_help(self):
        self.cmdline_parser.print_help()
        self.pause()

    @staticmethod
    def pause():
        print('\n')
        input("Press enter key to continue...")

    def make_directory(self, directory_name):
        if not os.path.exists(directory_name):
            try:
                os.mkdir(directory_name)
                self.log.info("Created directory {0}".format(directory_name))
            except OSError as e:
                self.log.error("Failed to create log directory {0} due to {1}.".format(directory_name, e.strerror))
                raise e

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        if value is not None:
            self._log = value
        else:
            self._log = logging.getLogger(__name__)
            self._log.warning("No logger provided. Initialised logger {0}".format(__name__))
