from .tasks.launch import Launch
from .tasks.open_project import OpenProject


def start():
    Launch.run()
    OpenProject.run()