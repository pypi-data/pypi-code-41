#This module tells current date and time with high accuracy
#output is in voice form
import datetime
from tuesday import speech
import pyttsx3

#Tells time
def time():
    #Format of time is set
    strtime=datetime.datetime.now().strftime("%H:%M:%S")   
    
    speech.speak(f"the time is {strtime}")
    print(strtime) 
#Tells date    
def date():
    date_object = datetime.date.today()
    speech.speak(f"today's date is {date_object}") 
    print(date_object)   
    