import sys
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from venv_clean.core.ui.venvview import VenvView


def play(screen, scene, path):
    scenes = [
        Scene([VenvView(screen, path)], -1, name="Main"),
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


def run(path):
    last_scene = None
    while True:
        try:
            Screen.wrapper(play, arguments=[last_scene, path])
            sys.exit(0)
        except ResizeScreenError as e:
            print('ResizeScreenError')
            last_scene = e.scene
        except KeyboardInterrupt:
            break
