import string
import pyautogui as pyautogui
import cv2 # locate image confidece support
from script.utils.utils import resource_path

secs_between_keys = 0.1

class Ui_tools:

    @staticmethod
    def getPosition(image: string):
        return pyautogui.locateCenterOnScreen(image, grayscale=True, confidence=.9)

    @staticmethod
    def click(position: tuple):
        pyautogui.click(position[0], position[1], 1, button='left')

    @staticmethod
    def click_on(ref: str):
        position = Ui_tools.getPosition(resource_path(ref))
        Ui_tools.click(position)

    @staticmethod
    def hot_key(*arg):
        pyautogui.hotkey(arg)

    @staticmethod
    def type(text: string):
        pyautogui.typewrite([text], interval=secs_between_keys)
