import pyautogui as pyautogui
import string
from ..utils.utils import resource_path
from ..utils.utils import split
from time import sleep

secs_between_keys = 0.1
secs_after_action = 0.1

class Ui_tools:

    @staticmethod
    def getPosition(image: string):
        try:
            return pyautogui.locateCenterOnScreen(image, grayscale=True, confidence=.8)
        except:
            return None

    @staticmethod
    def click(position: tuple):
        pyautogui.click(position[0], position[1], 1, button='left')
        sleep(secs_after_action)

    @staticmethod
    def click_on(ref: str):
        position = Ui_tools.getPosition(resource_path(ref))
        Ui_tools.click(position)
        sleep(secs_after_action)

    @staticmethod
    def hot_key(*arg):
        pyautogui.hotkey(*arg)
        sleep(secs_after_action)

    @staticmethod
    def type(text: string):
        pyautogui.typewrite(split(text), interval=secs_between_keys)
        sleep(secs_after_action)
