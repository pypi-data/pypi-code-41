"""This module enables automatic logins to sites without your interaction
"""


from tuesday import speech
import time
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from getpass import getpass


def facebooknum():
        """login facebook by number
        """
        speech.speak("say your number!")
                
        #user voice is taken as input       
        r=sr.Recognizer()
        r.energy_threshold=3000
        with sr.Microphone() as source:
                audio=r.listen(source)
                try:
                        n=r.recognize_google(audio,language='en-IN')
                        print(n)
                        speech.speak("type your password")
                        b=getpass("your password:")
                        speech.speak("processing your request") 
                        time.sleep(2)
                        driver=webdriver.Chrome()
                        driver.get("https://www.facebook.com/")
                        time.sleep(2)
                        yourphone=driver.find_element_by_xpath("//*[@id='email']")
                        yourphone.send_keys(n)
                        time.sleep(2)
                        pswd=driver.find_element_by_xpath("//*[@id='pass']")
                                
                                
                        pswd.send_keys(b)
                        time.sleep(4)
                        login=driver.find_element_by_xpath("//*[@id='u_0_a']")
                        login.click()
                        login=driver.find_element_by_xpath("//*[@id='u_0_2']")
                        login.click()
                        speech.speak("press ENTER to close")
                        input('Press ENTER to exit')
                except:
                        speech.speak("unable to process your request")               
def facebookemail():
        """login facebook by email
        """
        speech.speak("write your mail id")
        a=input("mail id:")
        speech.speak("write your password")
        b=getpass("password:")
        speech.speak("processing your request") 
        driver=webdriver.Chrome()
        driver.get("https://www.facebook.com/")
        time.sleep(2)
        yourphone=driver.find_element_by_xpath("//*[@id='email']")
        yourphone.send_keys(a)
        time.sleep(2)
        pswd=driver.find_element_by_xpath("//*[@id='pass']")
                        
                        
        pswd.send_keys(b)
        time.sleep(3)
        
        login=driver.find_element_by_xpath("//*[@id='u_0_a']")
        login.click()
        login=driver.find_element_by_xpath("//*[@id='u_0_2']")
        login.click()

        speech.speak("press ENTER to close")
        input('Press ENTER to exit')
                        
def gmail():
        """login gmail very easily
        """
        speech.speak("enter your email address!")
        a=input("mail id:")
        speech.speak("password")
        b=getpass("password:")
        speech.speak("processing your request")     
        driver=webdriver.Chrome()
        driver.get("https://accounts.google.com/signin/v2/identifier?service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
        time.sleep(2)
        email=driver.find_element_by_xpath("//*[@id='identifierId']")
        email.send_keys(a)
        n=driver.find_element_by_xpath("//*[@id='identifierNext']")
        n.click()
        time.sleep(2)
                        
        passw=driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
        passw.send_keys(b)
        time.sleep(2)
        m=driver.find_element_by_xpath("//*[@id='passwordNext']")
        m.click()
        speech.speak("press ENTER to close")
        input('Press ENTER to exit')                