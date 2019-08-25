"""Easy way to store data
"""
import speech_recognition as sr
from tuesday import speech


def create():
        """CREATE a file by your VOICE"""
        speech.speak("name the file ")
        r=sr.Recognizer()
        r.energy_threshold=3000
        with sr.Microphone() as source:
                print("listening....")
                r.pause_threshold=1
                audio=r.listen(source)
                try:  
                        s=r.recognize_google(audio,language='en-IN')
                        print(s)
                        text=s+".txt"

                        f=open(text,"x")
                        f.close()

                        f=open(text,"a")
                
                                       
                
                
                        with sr.Microphone() as source:
                                speech.speak("speak the content")
                                print("listening....")
                                r.pause_threshold=1
                                audio=r.listen(source)
                                print("recognising...")
                                
                                p=r.recognize_google(audio,language='en-IN')
                                print("user said:",p)
                                f.write(p)
                                f.close()
                except:
                        speech.speak("can't recognize")        
def edit():
        """EDIT a file data 
        """
        speech.speak("name of the file")
        r=sr.Recognizer()
        r.energy_threshold=3000
        with sr.Microphone() as source:
                print("listening....")
                r.pause_threshold=1
                audio=r.listen(source)
                try:
                        s=r.recognize_google(audio,language='en-IN')
                        text=s+".txt"
                        f=open(text,"a")
                        
                        with sr.Microphone() as source:
                                speech.speak("say")
                                print("listening....")
                                r.pause_threshold=1
                                
                                audio=r.listen(source)
                                print("recognising...")
                        
                                p=r.recognize_google(audio,language='en-IN')
                                print("user said:",p)
                                f.write(p)
                                f.close()
                except:
                        speech.speak("can't recognize")        
        speech.speak("press ENTER to close")
        input('Press ENTER to exit')             
def access():
        """ACCESS data stored in the file
        """
        speech.speak("name of the file")
        r=sr.Recognizer()
        r.energy_threshold=3000
        with sr.Microphone() as source:
                print("listening....")
                r.pause_threshold=1
                audio=r.listen(source)
                try:
                        s=r.recognize_google(audio,language="en-IN")
                        print(s)
                        text=s+".txt"
                        f=open(text,"r")
                        t=f.readlines()
                        speech.speak(t)    
                        print(t)     
                        f.close()
                        speech.speak("press ENTER to close")
                        input('Press ENTER to exit')
                except:
                        speech.speak("can't recognize")        
         