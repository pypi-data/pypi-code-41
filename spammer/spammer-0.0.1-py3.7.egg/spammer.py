import pyautogui
import time
import random
import threading
print("module lancer")
def aide(nothing):
        print('for minecraft spamming write this for exemple : minecraft(3,"mineraft spammings"",10,0.5)')
def spam(text, number, delay):
        time.sleep(5)
        def start():
                for x in range(0,number):
                        r = str(random.randint(10, 99999999999999999999999999999999999999999999999999999))
                        pyautogui.typewrite(r)
                        
                        pyautogui.typewrite(["enter"])
                        time.sleep(temp)
        

def minecraft(text, number, temp):
        time.sleep(5)
        if text == random:
                for x in range(0,number):
                        r = str(random.randint(10, 99999999999999999999999999999999999999999999999999999))
                        pyautogui.typewrite("t")
                        pyautogui.typewrite(r)
                                
                        pyautogui.typewrite(["enter"])
                        time.sleep(temp)
        else:
                for x in range(number):
                        r = str(random.randint(1, 9))
                        pyautogui.typewrite("t")
                        pyautogui.typewrite(text + r)
                        time.sleep(temp)
                        pyautogui.typewrite(["enter"])   
           
