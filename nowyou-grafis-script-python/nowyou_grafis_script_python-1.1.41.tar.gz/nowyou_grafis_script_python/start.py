from .tasks.grading import Grading
from .tasks.launch import Launch
from .tasks.project import Project


def start():
    Launch.run()
    Project.open_project()
    Grading.run()
    Project.save_project()
