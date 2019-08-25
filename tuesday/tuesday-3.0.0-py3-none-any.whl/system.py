"""Controls SHUTDOWN , RESTART  of system and open file or execute file 
"""
import os
import speech_recognition as sr
from tuesday import speech


def shutdown():
    """Shutdown the system
    """
    speech.speak("goodnight sir!")
    os.system("shutdown /s /t 1")
def restart():
    """Restart the system
    """
    speech.speak("restarting sir")
    os.system("shutdown /r /t 1")  
def openfile(path):
    """Open file according to given path
    """
    os.startfile(path)    
