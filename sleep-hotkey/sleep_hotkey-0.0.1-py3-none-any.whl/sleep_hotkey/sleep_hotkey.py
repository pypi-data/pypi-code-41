import keyboard
import time

DEFAULT_LOOP_INTERVAL = 2
DEFAULT_EXIT_KEY = 'esc'


def sleep(seconds, loop_interval=DEFAULT_LOOP_INTERVAL, exit_key=DEFAULT_EXIT_KEY):
    while not keyboard.is_pressed(exit_key):
        if seconds >= loop_interval:
            time.sleep(loop_interval)
            seconds -= loop_interval
        else:
            time.sleep(seconds)
            break
