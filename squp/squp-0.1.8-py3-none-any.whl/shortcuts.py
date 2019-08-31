'''
File that contains commonly used shortcuts for utilities in basic python and selenium
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

# Globals
browser = None

## Initialize the browser to ensure security
def set_browser(b):
    global browser
    browser =  b
    
def get_browser():
    global browser
    return browser

#### Selenium Selection Shortcut Methods ####

## Attribute Selectors ##
# Returns the item with the given name attribute from the browser
def name(n):
    # Get the browser
    global browser
    return browser.find_element_by_name(n)

## CSS Document Selectors ##
# Returns the element designated by the css selector
def css(sel):
    # Get the browser
    global browser
    try:
        return browser.find_element_by_css_selector(sel)
    except:
        return browser.find_by_css(sel)

# Returns the element designated by the css selector
def csss(sel):
    # Get the browser
    global browser
    return browser.find_elements_by_css_selector(sel)
    
## CSS Element Base Selectors ##
# Returns the element designated by the css selector
def Css(el, sel):
    return el.find_elements_by_css_selector(sel)

## XPath Document Base Selectors ##
# Returns the element designated by the xpath selector
def xpath(sel):
    # Get the browser
    global browser
    try:
        return browser.find_element_by_xpath(sel)
    except:
        return browser.find_by_xpath(sel)
    
# Returns the elements designated by the xpath selector
def xpaths(sel):
    # Get the browser
    global browser
    return browser.find_elements_by_xpath(sel)
    
## XPath Element Base Selectors ##
# Returns the element designated by the xpath selector starting at the given element
def Xpath(el, sel):
    return el.find_element_by_xpath(sel)
    
# Returns the element designated by the xpath selector starting at the given element
def Xpaths(el, sel):
    return el.find_elements_by_xpath(sel)

#### Resting Methods ####

## Default Resting ##
# Makes the program sleep for half a second
def slp(t=0.5):
    time.sleep(t)

## Indicated Time Resting ##
# Lets the program rest for a specified period of time
def rest(tm):
    time.sleep(tm)
