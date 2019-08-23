from tasks.open_project import OpenProject
from script.tasks.launch import Launch


def start():
    Launch.run()
    OpenProject.run()
