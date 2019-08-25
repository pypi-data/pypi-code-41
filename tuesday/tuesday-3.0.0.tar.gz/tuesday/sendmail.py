#This module sends mail using your speech 
#User words are directly send as message
from tuesday import speech
# speech module includes speak function
#getpass module hides the given input
#maintains privacy
from getpass import getpass
import speech_recognition as sr
#simple mail transfer protocol 
import smtplib


def send():
    """Email is send by user VOICE
    """
    try:
        speech.speak("enter your email address!")
        b=input("mail id:")
        speech.speak("password sir")
        a=getpass("password:")
        #SMTP function from smtplib 
        server = smtplib.SMTP('smtp.gmail.com',587)#587 is port number
        server.ehlo()
        server.starttls()
        server.login(b, a)
        speech.speak("to whom sir")
        to = input("mail id:")
        #message to be sent is taken as input
        r=sr.Recognizer()
        r.energy_threshold=5000
        with sr.Microphone() as source:
            speech.speak("What should I say?")
            print("listening...")

            audio=r.listen(source) 
            print("recognizing...") 
            s=r.recognize_google(audio,language='en-IN')
            print(s)
        server.sendmail(b, to, s)
        speech.speak("email sent")
        #necessory to close
        server.close()    
    except Exception as e:
        print(e)
        speech.speak("email not sent")