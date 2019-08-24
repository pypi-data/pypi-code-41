import tasks.open_project as open_project
import tasks.launch as launch


def start():
    launch.Launch.run()
    open_project.OpenProject.run()
