'''
interface.py
Version: 1.0.2
Author: Jonathan Hoyle
Product Name: SqUp (Squarespace Uploader, pronounced "Scoop")
Description:
    An artificial intelligence agent that adds, updates, removes, and otherwise manages information previously
        entered onto a Squarespace storefront.
    In particular, this file is the actual interface between a bot "user" and the Squarespace interface.
        In other words, this file does the hard work of actually editing, uploading, and managing information on the website.
    This version uses a data file parsed from the other separate pieces of this program to compare old
    store data and new scraped data, and then update the old data based on what the new data contains.
Planned or Possible:
    - Condensation of code via creation of methods that perform certain overall processes
        + In short, generalizing some of the code found here, particularly in addNewItems
        + Basically a more concrete version of the general shortcut, movement, and update methods created at the beginning of this program
    - In short, a complete and total rewrite of this program for optimization and lack of redundancy in code, focusing mainly on the following:
        + adding new items
        + updating old items
        + properly implementing Splinter interface
    - Arrangement of items for simplicity of both a user and the agent, allowing an agent to stop after looking at a
        certain number of items, since all of the items thereafter would be hidden
        + Will require re-arrangement methods
        + Possibly intelligently sorting as well based on images(?)
        + Very late-development stuff

Note that for references/outside sources, all exterior code and material belongs to their respective owners
'''

#TODO: Set up command line utilities for different methods here (i.e. given json/name, do this command)

# ---------------------- BEGIN IMPORTS ----------------------

# noinspection PyUnresolvedReferences
# noinspection PyPackageRequirements
import time, re, json, urllib, urllib.request, urllib.parse, urllib.error, unicodedata, colour, atexit, logging, \
    information, os, sys, scrapy, importlib, ftfy
from collections import namedtuple
# noinspection PyPackageRequirements
from selenium import webdriver
# noinspection PyPackageRequirements
from selenium.common import exceptions
# noinspection PyUnresolvedReferences
# noinspection PyPackageRequirements
from selenium.common.exceptions import TimeoutException
# noinspection PyPackageRequirements
from selenium.webdriver.chrome.options import Options
# noinspection PyPackageRequirements
from selenium.webdriver.common.action_chains import ActionChains
# noinspection PyPackageRequirements
from selenium.webdriver.common.keys import Keys
# noinspection PyPackageRequirements
from selenium.webdriver.common.by import By
# noinspection PyPackageRequirements
from selenium.webdriver.support import expected_conditions as EC
# noinspection PyPackageRequirements
from selenium.webdriver.support.ui import WebDriverWait
# noinspection PyPackageRequirements
from PIL import Image
# noinspection PyPackageRequirements
import numpy as np
# noinspection PyPackageRequirements
from DataConversion import Conversion
# noinspection PyUnresolvedReferences
from information import Info
from datetime import date, datetime
# noinspection PyPackageRequirements
from splinter import Browser
from splinter.element_list import ElementList
import SplinterShortcuts as SpS
# noinspection PyUnresolvedReferences
import SystemShortcuts as SyS
from ahk import AHK

# ----------------------- END IMPORTS -----------------------

# ----------------- BEGIN GLOBAL VARIABLES ------------------

# region Globals

# Get the current time and date (ctd) as a string (str) for the logger
ctd_str = time.strftime('%m_%d_%y__%H_%M_%S.log', time.localtime())
# Set the logger up
logging.basicConfig(filename=ctd_str, level=logging.DEBUG)

# Browser setup
opts = Options()
opts.add_argument("--window-size=1920,1080")
'''
# Headless window initialization, easier to intialize, yet less dependable for unknown reasons
browser = Browser('chrome', headless=True, options=opts)
'''
# Headed window implementation, extra work to initialize cleanly, yet passes most if not all tests
# Import pyautogui
import pyautogui as pa

# Initialize the browser
try:
    browser = Browser('chrome', options=opts)
except:
    SpS.update_driver()
    browser = Browser('chrome', options=opts)
SyS.slp(.5)
# Create a counter of tries
bad_counter = 0
# Create an AutoHotKey object
ahk = AHK()
# Find the list of all open windows
win = list(ahk.windows())
# Loop through the windows and activate the currently empty browser
for i in range(len(win)):
    if b'data:' in win[i].title:
        win[i].activate()
        pa.keyDown('win')
        pa.keyDown('h')
        pa.keyUp('h')
        pa.keyUp('win')
        break
# Save the mouse's original position
#old_mouse = pa.position()
# Python used Pound!
#pa.click(coords[0], coords[1])
# Python used Minimize!
# Python used Teleport!
#pa.moveTo(old_mouse[0], old_mouse[1])
# Python used Rest!
SyS.slp3()
# Create a counter of tries
bad_counter = 0
# Reset the coordinates variable
coords = None
for w in win:
    if b'Python' in w.title and b'chromedriver' in w.title:
        w.activate()
        SyS.slp(0.2)
        pa.keyDown('win')
        pa.keyDown('h')
        pa.keyUp('h')
        pa.keyUp('win')
        break
# If the program was not run using a debugger (legacy)
'''if sys.gettrace() is None:
    # While it hasn't been running for more than two and a half seconds
    while bad_counter < 25 and coords is None:
        # Try updating the coordinates
        try:
            coords = list(pa.locateAllOnScreen('imgs/ChromeOpenedCmdPart.png'))[0]
        # If that doesn't work
        except:
            # Increment the counter
            bad_counter += 1
            # Python used Rest!
            SyS.slp(0.1)
# If the coordinates have been found
if coords is not None:
    # Send the console window to the alternate desktop
    pa.click(coords[0], coords[1])
    pa.keyDown('win')
    pa.keyDown('h')
    pa.keyUp('h')
    pa.keyUp('win')
    # Move the mouse back to its original position
    pa.moveTo(old_mouse[0], old_mouse[1])
    # Python used Rest!
    SyS.slp(1)
# except:
#    pass

# '''
SpS.set_browser(browser)

# Selenium webdriver
# browser = s_browser.driver
# Maximize window (for testing only)
# browser.maximize_window()

# All product names currently in the store
all_names = []
# All product names added in a new update
new_names = []
# All products that were moved
all_moved_names = []
# All known colors
known_colors = []
# Individual words from knownColors
kI = []

# All urls for admin store pages (mainly for product name location)
urls = ['https://brent-cline-7fyn.squarespace.com/config/pages/530dd538e4b07f28cd98d45b']
admin_urls = {'STORE_PAGE': 'https://brent-cline-7fyn.squarespace.com/config/pages/530dd538e4b07f28cd98d45b'}

# Indicates whether login has occurred or not
logged_in = False


# Method to check if logged in
def check_logged_in():
    return logged_in


# Global variable to hold all relevant items
# relItems = {}
jda = {}
jdn = {}
Item = None

# Global variables to allow for indicating that a form is needed
form_needed = False
fit_form_needed = False
l_form_needed = False
unf_form_needed = False

# Global variables for sizes
shoe_sizes = []
shirt_sizes = []
pant_sizes = []
widths = []

# Global variables for brands where inventory matters
inventory_dependents = ['Smathers & Branson']

# Variables for determining season in adding new seasonal items
# Dummy leap year to allow input X-02-29 (leap day)
Y = 2000
# Defining seasons
seasons = [('Winter', (date(Y, 1, 1), date(Y, 3, 20))),
           ('Spring', (date(Y, 3, 21), date(Y, 6, 20))),
           ('Summer', (date(Y, 6, 21), date(Y, 9, 22))),
           ('Autumn', (date(Y, 9, 23), date(Y, 12, 20))),
           ('Winter', (date(Y, 12, 21), date(Y, 12, 31)))]

# Origin names
origins = []
marked = False


# Initialize this class/file/whateveritissinceitsnotanactualclass
def __init__():
    # Get the current urls
    get_current_urls()
    # Direct the browser to the base page
    browser.visit(Info.STORE_PAGE)
    # And login
    SpS.complete_login()


# Non-default method for initialization, identical to above
def init():
    # Get the current urls
    get_current_urls()
    # Direct the browser to the base page
    browser.visit(Info.STORE_PAGE)
    # And login
    SpS.complete_login()


# endregion

# ------------------ END GLOBAL VARIABLES -------------------

# ---------------- BEGIN DECORATOR CLASSES ------------------

class LoginCheck:
    '''
    This class checks whether a user
    has logged in properly via
    the global "check_function". If so,
    the requested routine is called.
    Otherwise, it logs in then does
    the same
    '''
    
    def __init__(self, f):
        self._f = f
    
    def __call__(self, *args):
        logged_in = check_logged_in()
        if logged_in is 1:
            return self._f(*args)
        else:
            login()
            return self._f(*args)


# ----------------- END DECORATOR CLASSES -------------------

# ---------------- BEGIN SHORTCUT METHODS -------------------

# region Shortcuts

# Gets product names from all store pages
#@LoginCheck
def get_all_product_names():
    global urls, logged_in
    itemNames = []
    get_current_urls()
    currentUrl = browser.url
    if currentUrl != Info.STORE_PAGE:
        browser.visit(Info.STORE_PAGE)
        currentUrl = Info.STORE_PAGE
    for u in urls:
        browser.visit(u)
        SyS.slp(4)
        tempNames = SpS.get_item_names()
        for t in tempNames:
            if t not in itemNames:
                itemNames.append(t)
    browser.visit(currentUrl)
    return itemNames


# Gets all of the current urls
def get_current_urls():
    # Grab the globals
    global urls, admin_urls
    # Grab the page names
    pn = get_page_names()
    # For each page name
    for p in pn:
        # Create a temporary url variable
        tempUrl = None
        # Use the exec command to append the current page's url to urls...
        exec('urls.append(Info.' + p + ')')
        # And assign the temporary variable to that url as well
        exec('tempUrl = Info.' + p)
        # As long as everything went okay...
        if tempUrl is not None:
            # Use exec to add the variable and its value to adminUrls
            exec('newDefault = admin_urls.setdefault(p, "")')
            admin_urls[p] = tempUrl
    temp_urls = []
    for tu in urls:
        if tu not in temp_urls:
            temp_urls.append(tu)
    urls = temp_urls
    # Finally, since it's not in the previous parse, add the store page and its url as the default entry
    admin_urls.setdefault('STORE_PAGE', '')
    admin_urls['STORE_PAGE'] = 'https://brent-cline-7fyn.squarespace.com/config/pages/530dd538e4b07f28cd98d45b'


# Gets all possible options from inventory.py
def get_page_names():
    # Open the file
    f = open('information.py', 'r')
    # Store the lines of the file
    lines = f.readlines()
    # Close the file
    f.close()
    # Set a start variable for when parsing begins
    startVariables = False
    # Create the dict of variable names
    variableNames = {}
    # Go through all of the file lines
    for l in lines:
        # Once it hits the right line, begin parsing
        if l == '  #BEGIN IPS\n':
            startVariables = True
            # Python used Future Sight!
            continue
        if startVariables:
            sides = l.split(' = ')
            rhsTokens = sides[0].split('_')
            nameTokens = rhsTokens[2:]
            variableNames[sides[0][2:]] = nameTokens
    return variableNames


# Logs in to the home page once there
def login(already_tried=False):  # Get the browser
    global browser, s_browser, logged_in
    try:
        # Send the email for the login to the email field
        browser.fill('email', Info.LOGIN)
        # Python used Rest!
        SyS.slp(.5)
        # Send the password for the login to the password field
        browser.fill('password', Info.PWD)
        # Send the Enter key to the password field to submit
        browser.find_by_text('Log In').click()
        # Python used Rest!
        SyS.slp(.5)
        # Indicate that the browser is logged in
        logged_in = True
    except:
        if not logged_in and not already_tried:
            # Reload the page
            browser.visit(Info.STORE_PAGE)
            # Python used Rest!
            SyS.slp(3)
            # Try to login again
            login(already_tried=True)


# endregion

# ----------------- END SHORTCUT METHODS --------------------

# ---------------- BEGIN UTILITY METHODS --------------------

# region Utility

# Replaces the current browser with the supplied one
def replace_browser(rep_b):
    # Grab the global browser
    global browser
    # Check if the supplied variable is the right typing
    if type(rep_b) is type(browser):
        # Close the current browser
        browser.quit()
        # And replace the browser
        browser = rep_b


# Returns two lists, one for pants widths and one for pants lengths
def format_pants(ps):
    # Create the lists for the results
    w_s = []
    l_s = []
    # If the list has not already been split, split it
    if 'x' in ps[0]:
        # Create an list for the split sizes
        p_s = []
        # For each entry
        for p in ps:
            # Append the split version to the new list
            p_s.append(p.split(' x '))
        # Set the original variable to this new information
        ps = p_s
    # For each size variable
    for p in ps:
        # If the width isn't already counted
        if p[0] not in w_s:
            # Count it
            w_s.append(p[0])
        # If the length isn't already counted
        if p[1] not in l_s:
            # Count it
            l_s.append(p[1])
    # Return the width and length lists
    return w_s, l_s


# Generalizes the given item's name
def generalize(i_n):
    # Grab the globals needed
    global jda, origins
    new_name = i_n
    # If origins hasn't been initiated yet
    if len(origins) == 0:
        # Find the origins of all of the items
        for i in jda:
            # If the origin company is not already included
            if jda[i]['origin'] not in origins:
                # Initalize that origin company
                origins.append(jda[i]['origin'])
    new_name = ftfy.fix_text(new_name)
    for o in origins:
        new_name = new_name.replace(o + ' ', '')
        new_name = new_name.replace(o, '')
    new_name = new_name.replace('Copy of ', '')
    return ftfy.fix_text(new_name.strip())


# Returns the base website that the corresponding item should be updated from in case of emergencies
def get_base_site(i):
    origins = {'Southern Tide': 'http://www.southerntide.com/', 'Psycho Bunny': 'http://www.psychobunny.com/',
               'David Donahue': 'https://www.daviddonahue.com/shirts?list=9999'}
    return origins[i['origin']]


# Gets the colors that will be recognized during the parsing process
def get_color_names():
    # Reference the global colors known
    global known_colors, kI
    # Reset just in case
    known_colors = []
    # For everything in the list used to convert RGB values to names
    for a in colour.RGB_TO_COLOR_NAMES:
        # And each name that goes with it
        for b in colour.RGB_TO_COLOR_NAMES[a]:
            # Append that string to the known colors
            known_colors.append(b)
    # For the now obtained strs, begin formatting
    for a in known_colors:
        # Create a temporary string to hold the formatting
        currentString = ''
        # For each character in the str
        for b in a:
            # If it's upper case
            if b.isupper():
                # Add a space
                currentString += ' ' + b
            # Otherwise
            else:
                # Just add the char
                currentString += b
        # Set the current index of the known colors to this new formatted str
        known_colors[known_colors.index(a)] = currentString
    # Lastly, for each entry in the newly formatted colors
    for a in known_colors:
        # Remove the first space that results from the above parsing in each entry
        known_colors[known_colors.index(a)] = a[1:]
    # Now separate individual names from the others, and add those to the individuals list kI
    for k in known_colors:
        # If there's more than one word in this color
        if ' ' in k:
            # For each word in this color
            for k1 in k.split(' '):
                # As long as it's not already listed
                if k1 not in kI:
                    # Add it to the list
                    kI.append(k1)
        # If it's just one word
        else:
            # And it's not already listed
            if k not in kI:
                # Then list it
                kI.append(k)


# Returns the current season of the year at the date given
def get_season(now):
    global Y, seasons
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)


# Returns whether the string is numeric or not
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# Returns the most common color (other than white obviously) of a given item
def find_closest_color(im):
    # Make this into an image if it's not one (i.e. the path was given)
    if type(im) != Image:
        try:
            im = Image.open(im)
        except:
            im = Image.open('C://imgJson//full//' + str(im))
    # Create an array for the closest colors to each pixel in the image
    closest_colors = []
    # Loop through the width
    for w in range(0, im.width):
        # And height
        for h in range(0, im.height):
            # Get the current pixel
            cp = im.getpixel((w, h))
            # And append the closest color to that pixel to the list
            closest_colors.append(ColorNames.findNearestImageMagickColorName(cp))
    # Create the final array of colors
    cn = []
    # Loop through all of the previous colors
    for c in closest_colors:
        # As long as the pixel isn't pure white
        if c != 'white':
            # Append it to the final list
            cn.append(c)
    # Return the most common element from the final list
    return max(set(cn), key=cn.count)


# endregion

# ------------------ END UTILITY METHODS --------------------

# ----------------- BEGIN COMPARE METHODS -------------------

# region Compare

# Getting size information out of the color field
# Number sizes, specifically for use in shoes sizes
def numC(c):
    # Grab the global shoeSizes variable
    global shoe_sizes, pant_sizes
    # Check to see if the size contains a number and thus is not a shirt
    # If the letter x is not in the size, then it must be a shoe size
    if (
            '1' in c or '2' in c or '3' in c or '4' in c or '5' in c or '6' in c or '7' in c or '8' in c or '9' in c or '0' in c) and (
            'x' not in c):
        shoe_sizes.append(c)
        # Return that this is a shoe or pant size
        return True
    # If the letter x is a shoe size, then it must be a pant size
    elif (
            '1' in c or '2' in c or '3' in c or '4' in c or '5' in c or '6' in c or '7' in c or '8' in c or '9' in c or '0' in c) and (
            'x' in c):
        pant_sizes.append(c)
        # Return that this is a shoe or pant size
        return True
    # Otherwise indicate a shirt size
    else:
        return False


# Letter Sizes, handles anything from XS to XXXL
def sizeC(c):
    # Grab the global shirtSizes variable
    global shirt_sizes
    # If the size fits the parameters for the a shirt, mark it as a shirt
    if len(c) == 1 or len(c) == 2 or (len(c) == 3 and (c != 'Sky' and c != 'Red' and c != 'Fig' and c != 'Rio')) or (
            len(
                c) == 4 and 'XXX' in c) or 'Fit' in c or '30L' in c or '32L' in c or '34L' in c and c not in shirt_sizes:
        # Add it to the shirtSizes
        shirt_sizes.append(c)
        return True
    # If the word Fit is in the size, then mark it for a fit form requirement
    elif ' Fit' in c:
        global fit_form_needed
        fit_form_needed = True
        return True
    # Another possible shirt size
    elif ' UNF' in c:
        return True
    # If nothing matches, return that it's not a shirt size
    else:
        return False


# endregion

# ------------------ END COMPARE METHODS --------------------

# ----------------- BEGIN UPDATE METHODS --------------------

# region Update

### Initialization ###
# This is the start of the update process for a single item, exact protocols and methods follow
#@LoginCheck
def update(name):
    # Do the necessary action to start the update
    try:
        SpS.select_item(SpS.item_name(name))
    except:
        SpS.select_item(SpS.item_name(name)[0])
    SyS.slp(3.0)
    return True


### First Options Page ###
# region First Options Page
# Methods that update elements on the first options page
# Updates product description (Base Confirmed)
def updateDesc(name):
    # Grab the globals
    global jda
    # Get the description that we need to put in
    newDesc = ''
    try:
        newDesc = SyS.other_people(jda[name]['description'], jda[name]['origin']).strip()
    except:
        newDesc = SyS.other_people(jda[name]['description']).strip()
    # Python used Rest!
    print(newDesc)
    SyS.slp3()
    # Before officially changing the contents, we check to see if the string is empty
    if newDesc.strip() == '':
        # If it is, then open a new browser
        temp_browser = webdriver.PhantomJS()
        # Format the current name to fit the url we need
        # Make it lowercase
        f_name = name.lower()
        # Replace spaces with underscores
        f_name = re.sub(' ', '-', f_name)
        # Navigate to the page of this item
        temp_browser.get('http://www.southerntide.com/' + f_name)
        try:
            # Assign the value of the found element to the variable
            newDesc = WebDriverWait(temp_browser, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@id="description"]'))).text
            try:
                newDesc = SyS.other_people(jda[name]['description'], jda[name]['origin']).strip()
            except:
                newDesc = SyS.other_people(jda[name]['description']).strip()
        except:
            pass
        temp_browser.quit()
    # Then send it to the field
    desc = SpS.xpath('//iframe[@tabindex=0]')
    # Python used Pound!
    desc.click()
    SpS.select_all_and_erase(desc)
    # Python used Rest!
    SyS.slp3()
    if newDesc != '':
        desc.type(newDesc.replace('&nbsp;', ''))
    # After we enter the new descriptions, parse tags out of the description
    parsedTags = []
    if 'Southern Tide' in newDesc:
        parsedTags.append('Southern Tide')


# Puts the given description in that field
def updateGivenDesc(newDesc, origin):
    # Send it to the field
    desc = SpS.xpath('//div[contains(@class, "TextEditor-editor-1W6me")]')[0]
    # Python used Pound!
    try:
        desc.click()
    except:
        ac = ActionChains(browser.driver)
        ac.click().perform()
    SpS.select_all_and_erase(desc)
    # desc.click()
    # Python used Rest!
    SyS.slp3()
    try:
        desc.type(SyS.other_people(newDesc, origin).replace('&nbsp;', ''))
    except:
        try:
            desc.type(SyS.other_people(newDesc).replace('&nbsp;', ''))
        except:
            pass


### Details Page ###
# Updates details (Confirmed)
def updateDetails(name):
    # Grab the globals needed
    global jda
    # Set the new details to an easy-to-reference variable
    newDets = jda[name]['details']
    # Click the details tab
    additionalTab = SpS.xpath('//div[contains(text(), "Additional")]')
    # Python used Pound!
    additionalTab.click()
    # Python used Rest!
    SyS.slp(2)
    # Reference the section where details are typed
    dets = SpS.css('div[role="textbox"]')
    # Erase what's currently there
    SpS.select_all_and_erase(dets[0])
    # Type the new ones in
    for d in newDets[:]:
        if len(d) > 2:
            dets[0].type('- ' + d + Keys.ENTER)
        # End the method here, since the saving and closing of the item occurs in the code that references this method


# Updates details (Confirmed)
def updateDetailsWithData(name, jd):
    # Set the new details to an easy-to-reference variable
    newDets = jd[name]['details']
    # Click the details tab
    additionalTab = SpS.xpath('//div[contains(text(), "Additional")]')
    # Python used Pound!
    additionalTab[0].click()
    # Python used Rest!
    SyS.slp(2)
    # Reference the section where details are typed
    dets = WebDriverWait(browser.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.sqs-editing.sqs-empty>div')))
    # Erase what's currently there
    SpS.select_all_and_erase(dets)
    # Click it
    dets.click()
    # Type the new ones in
    for d in newDets[:]:
        if len(d) > 2:
            dets.send_keys('- ' + d + Keys.ENTER)
        # End the method here, since the saving and closing of the item occurs in the code that references this method


# Updates tags and categories for each item
# For equal use both adding initially and updating existing
def updateTags(name):
    # Get the description in order to parse the tags from it
    # descriptionParse = other_people(jda[name]['description'])
    # Create a list of all of the words that we want to tag
    tagWords = ['Shirt', 'Polo', 'Sport', 'Southern Tide', 'Robert Graham', 'Psycho Bunny', 'Performance', 'Hat',
                'Visor', 'Heathered', 'Hoodie',
                'T-Shirt', 'T-shirt', 'Tee', 'Shorts', 'Swim', 'Trunk', 'Slick', 'Rain', 'Over', 'Pullover', 'Vest',
                'Watch',
                'Long Sleeve', 'Tie', 'Flipjacks', 'Flip-Flops', 'Bow Tie', 'Gameday', 'Belt', 'Boxer', 'Plaid',
                'Stripe', 'Caddie', 'Pants', 'Pant',
                'Chino', 'Trim', 'Jeans', 'Sweater', 'Knit', 'Jacket', 'Sweatshirt']
    # Separate the tag words into categories
    cats = {'Shirts': ['Shirt', 'Polo', 'Sport', 'T-Shirt', 'Long-Sleeve', 'T-shirt', 'Tee'],
            'Accessories': ['Hat', 'Visor', 'Belt', 'Tie', 'Flipjacks', 'Flip-Flops', 'Bow Tie', 'Boxer', 'Can ',
                            'Caddie', 'Watch'],
            'Outerwear': ['Hoodie', 'Rain', 'Slick', 'Vest', 'Over', 'Pullover', 'Sweater', 'Jacket', 'Sweatshirt'],
            'Swim': ['Swim', 'Trunk'],
            'Shorts': ['Cargo', 'Shorts'], 'Pants': ['Pants', 'Pant', 'Jeans']}
    try:
        if jda[name]['origin'] not in tagWords:
            tagWords.append(jda[name]['origin'])
    except:
        pass
    # To delete old tags, see the code in updateTagsGiven
    # Find the values of all of the current tags
    tagTexts = []
    # Try to assign it to the values of the tags
    try:
        currentTags = SpS.xpaths('//div[@class="tag"]')
        for c in currentTags:
            tagTexts.append(c.text)
    # If that doesn't work, don't worry about it
    except:
        pass
    # Log the values found
    logging.debug(tagTexts)
    # Create a variable for the category
    cat = ''
    # Determine this item's category
    for tagWord in tagWords:
        if tagWord in name:
            for c in cats:
                # Set the first tag that matches a category
                if tagWord in cats[c]:
                    # To the aforementioned category variable
                    cat = c
                    # Python used Brick Break!
                    break
    # Log the category
    logging.debug(cat)
    # Find the add tag button
    try:
        addTag = SpS.xpath('//div[@class="tag-field-container"]//div[@class="add-header"]')
        # Python used Pound!
        addTag.click()
        # Python used Rest!
        SyS.slp3()
        # Go through each word in the predefined tags
        for tagWord in tagWords:
            # Find the flyout text element that just came up/refreshed
            # Note that this element will be wrong if the category pops up, moved here because categories won't be parsed
            #    if there are no new tags to be added if left inside the if statement below
            tagIn = SpS.xpaths('//input[@class="field-input"]')[0]
            # If it's in there, start adding it
            # if name.find(tagWord) != -1:
            if tagWord in name and tagWord not in tagTexts:
                # Send the tag to it
                tagIn.type(tagWord + ',')
                # Python used Rest!
                SyS.slp3()
        # Finally, call this method again within itself to guarantee a failure the second time, allowing category to be set
        updateTags(name)
    # If this is running, that means it's clicked the category, so it should be the selection of a category now
    except:
        # Python used Rest!
        SyS.slp2()
        # If it clicks the wrong thing, do the category first, since it should be already up
        # Try to move to an already selected category
        try:
            # Just move to it and stop, if this fails, then a category needs to be assigned
            SpS.move_to(SpS.xpath('//div[@class="flyout-option category active"]'))
            # Python used Pound!
            SpS.move_and_click(SpS.xpath('//div[contains(text(), "Item")]'))
        # If there isn't such a category, assign one
        except:
            # Try to find and click the corresponding category
            try:
                # Find the element we want
                cs = WebDriverWait(browser.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "' + cat + '")]')))
                # Python used Pound!
                SpS.move_and_click(cs)
                # Python used Rest!
                SyS.slp3()
                # Python used Pound!
                SpS.move_and_click(SpS.xpath('//div[contains(text(), "Item")]'))
            # If it can't find it because it just doesn't like me
            except:
                # Python used Rest!
                SyS.slp3()
                # Find the last of all elements that match this one's SpS.xpath, and click it
                # Note that it should be last since it was the last one generated
                try:
                    # Python used Pound!
                    SpS.move_and_click(SpS.xpaths('//div[contains(text(), "' + cat + '")]')[-1])
                    # Python used Rest!
                    SyS.slp3()
                    # Python used Pound!
                    SpS.move_and_click(SpS.xpath('//div[contains(text(), "Item")]'))
                # If it's made it this far and fails, set the category to miscellaneous
                except:
                    try:
                        # Python used Pound!
                        SpS.move_and_click(SpS.xpaths('//div[contains(text(), "Accessories")]')[-1])
                        # Python used Rest!
                        SyS.slp3()
                        # Python used Pound!
                        SpS.move_and_click(SpS.xpath('//div[contains(text(), "Item")]'))
                    # If it fails now, it deserves to
                    except:
                        pass
        # Python used Rest!
        SyS.slp3()
        # Indicate whether or not the tags were started
        started = False
        # Create what will be the add tags button
        addTag = None
        # Go through each tag
        for tagWord in tagWords:
            # If it's in there, start adding it
            if tagWord in name and tagWord not in tagTexts:
                # Click the add button if there's something that should be there but isn't
                if not started:
                    # Click elsewhere so that the tag can be clicked if necessary
                    # Python used Pound!
                    SpS.move_and_click(SpS.xpath('//div[contains(text(), "Item")]'))
                    # Python used Rest!
                    SyS.slp(1)
                    try:
                        # Find the actual add tag
                        addTag = SpS.xpath('//div[contains(@class, "tag")]')[0]
                    except:
                        try:
                            addTag = SpS.xpaths('//input[@class="field-input"]')[0]
                        except:
                            pass
                    try:
                        addTag.click()
                        # Indicate that this doesn't need to happen any more
                        started = True
                    except:
                        pass
                try:
                    # Find the flyout text element that just came up/refreshed
                    tagIn = SpS.xpaths('//input[@class="field-input"]')[0]
                    # Send the tag to it
                    tagIn.type(tagWord + ',')
                    # Python used Rest!
                    if started:
                        # Python used Rest!
                        SyS.slp3()
                except:
                    pass
        # Python used Rest!
        SyS.slp3()


# Updates tags on an object when the description is given directly
# Currently deprecated
def updateTagsGiven(description):
    # Create a list of all of the words that we want to tag
    tagWords = ['Polo', 'Southern Tide', 'Sport', 'Performance', 'Hat', 'Visor', 'Heathered',
                'Hoodie', 'T-Shirt', 'Shorts', 'Swim', 'Slick', 'Rain', 'Over']
    # To delete old tags, use the following
    # Find the current tag-type objects
    # Create an empty object for the tags
    tags = None
    # Find the current tag-type objects
    try:
        tags = SpS.csss('div.tag')
        # If there are already tags there, we delete them
        if tags is not None:
            # Make sure that we are actually getting tags, not categories, by comparing y-values
            # Get the first value, which will be the y-value of the row
            tagY = tags[0].location['y']
            # Create a temporary list to hold all of the tags in
            tempTags = []
            # Add each tag with the right y-value to the temporary list
            for t in tags:
                if t.location['y'] == tagY:
                    tempTags.append(t)
            # Set the original tags variable to this new list of tags
            tags = tempTags
            # Delete the necessary tags
            for t in reversed(tempTags[:]):
                SpS.move_to(t)
                # Python used Rest!
                SyS.slp2()
                deleteTag = SpS.css('span.x')
                # Python used Pound!
                deleteTag.click()
    except:
        pass
    # Find the add tag button
    addTag = SpS.xpath('//div[@class="tag-field-container"]//div[@class="add-header"]')
    # Python used Pound!
    addTag.click()
    # Python used Rest!
    SyS.slp3()
    # Go through each word in the predefined tags
    for tagWord in tagWords:
        # If it's in there, start adding it
        # if description.find(tagWord) != -1:
        if tagWord in description:
            # Find the flyout text element that just came up
            tagIn = SpS.xpath('//input[@class="field-input"]')
            tagIn.type(tagWord + ',')
            SyS.slp3()


### The following is necessary for multiple reasons, but the main one is that color and images aren't exactly ###
### connected, so it makes more sense to just delete them all, and then upload them again                     ###
# Deletes all of the old images (Confirmed)
def deleteImages():
    # Get all of the images delete buttons
    deletes = SpS.csss('div.sqs-action-overlay.top>div.remove-image')
    # Create the confirm button
    confirm = None
    # For each button
    for d in deletes:
        # Try to click the button
        try:
            SpS.move_and_click(d)
        # If it doesn't work it's probably a reference problem, recreate the element entirely to solve this
        except:
            d = SpS.csss('div.sqs-action-overlay.top>div.remove-image')[0]
            SpS.move_and_click(d)
        # Try to find the confirm button when it comes up
        try:
            confirm = WebDriverWait(browser.driver, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.sqs-widgets-confirmation-content.clear>div.buttons>div:last-of-type')))
        # If it doesn't go through the first time, try it again
        except:
            # Python used Rest!
            SyS.slp(3)
            try:
                confirm = WebDriverWait(browser.driver, 3).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.sqs-widgets-confirmation-content.clear>div.buttons>div:last-of-type')))
            except:
                pass
        # Move to an click the confirm button
        try:
            confirm.click()
        except:
            pass
        # Python used Rest!
        SyS.slp(1)


# Adds all of the new images (Confirmed)
def addImages(name):
    # Get all of the new images
    images = jda[str(name)]['image_paths']
    # Combine each images url into a single input string
    totalImages = ''
    first = True
    # Simulate pressing enter by using a new line between each one
    for i in images:
        if not first:
            totalImages = totalImages + '\n' + 'C:/imgJson/' + i
        else:
            totalImages = 'C:/imgJson/' + i
        first = False
    try:
        # Find the image upload area
        imageAdd = SpS.xpath('//input[@type="file"]')[0]
        # Send the images
        imageAdd.type(totalImages)
    except:
        pass


# Adds the given images
def addImagesGiven(images):
    # Combine each images url into a single input string
    totalImages = ''
    first = True
    images2 = []
    imageAdd = None
    # Go through each given image and first give it the proper full path
    for i in images:
        logging.debug(i)
        images2.append('C:/imgJson/' + i)
    # Then go through and make the giant string
    for i in images2:
        # Don't do this the first time around, cause no one likes to start empty
        if not first:
            totalImages = totalImages + '\n' + i
        else:
            totalImages = i
        first = False
    # Find the image upload area
    try:
        imageAdd = SpS.xpath('//input[@type="file"]')
    except:
        if browser.is_element_present_by_css('div.product-grid-action-tray'):
            selected_element = SpS.css('div.sqs-content-item-product.selected')
            selected_element.click()
            SyS.slp(.05)
            selected_element.click()
            SyS.slp(2)
            imageAdd = SpS.xpath('//input[@type="file"]')
    # Send the images
    try:
        imageAdd.type(totalImages if type(totalImages) is not ElementList else totalImages[0])
    except:
        if len(imageAdd) != 0:
            imageAdd[0].type(totalImages if type(totalImages) is not ElementList else totalImages[0])


### NOTE: This method is technically on the first page, but may be involved across several pages, TBD
# Updates Images (Confirmed)
def updateImgs(name):
    deleteImages()
    addImages(name)


# endregion

### Second Options Page ###
# region Second Options Page
# Methods that update elements on the next options page (Variants)

# Returns the available size options for the product
### Must be run during the process of variant updating ###
# NOTE: Only handles variant sizes, future plans are to add form sizes as well (for pants, shoes, etc.)
# Returns a list of all sizes used by this item
def getSizes():
    # Find the size inputs from the form
    sizeInputs = SpS.xpaths('//input[@name="Size"]')
    # Set up an list for the sizes
    sizes = []
    # Go through each size input
    for s in sizeInputs:
        # If it's content isn't already there, add it
        if s['value'] not in sizes:
            sizes.append(s['value'])
    # Return the result
    return sizes


def get_skus():
    sku_inputs = SpS.xpaths('//input[@name="sku"]')
    skus = []
    for s in sku_inputs:
        if s['value'] not in skus:
            skus.append(s['value'])
    return skus


# Deletes old colors (Confirmed)
# noinspection PyUnresolvedReferences
def deleteColors(colors):
    # Find all of the rows for the item
    rows = browser.driver.find_elements_by_css_selector('div.sqs-variant-row-content>div.variant-row')
    # Use a current variable to reference location to prevent confusion after rows are deleted
    current = 0
    deleted = 0
    # If there are actually colors to replace
    if len(colors) > 0:
        # Check each row for the old colors
        for r in reversed(rows):
            # Make sure that the row is visible (and thus contains content)
            try:
                WebDriverWait(browser.driver, 3).until(EC.visibility_of_element_located(r))
            # If it isn't, scroll to make it so
            except:
                # Try executing the scroll script with the original element
                try:
                    # Executing script
                    SpS.runScript("return arguments[0].scrollIntoView();", r)
                # If the old element is stale, re-create it and try again
                except:
                    rows2 = browser.driver.find_elements_by_css_selector('div.sqs-variant-row-content>div.variant-row')[
                            ::-1]
                    r = rows2[current - deleted]
                    SpS.runScript("return arguments[0].scrollIntoView();", r)
            # Get the color of the current element
            currentColor = SpS.Xpath(r,
                                     '/div[@class="attributes"]/div[@name="Color"]//input[@name="Color"]').get_attribute(
                'value')
            # If the current color is in the old elements list, delete that variant
            if currentColor.lower() in [c.lower() for c in colors]:
                # Find the current delete button and Python used Pound!
                deleteCurrent = SpS.Xpath(r, '/div[@class="remove-variant"]')
                try:
                    deleteCurrent.click()
                except:
                    SpS.runScript("return arguments[0].scrollIntoView();", deleteCurrent)
                    deleteCurrent.click()
                # Wait for the dialog to come up, and Python used Pound! when it does
                WebDriverWait(browser.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="buttons"]/div[@tabindex=3]'))).click()
                # Python used Rest!
                SyS.slp(1.0)
                # Increment the amount of items deleted
                deleted += 1
            # Increment the current value
            current = current + 1


# Adds new colors (Confirmed)
def addColors(name, colors):
    # Set up the string translation for later
    # all = string.maketrans('','')
    # nodigs = all.translate(all, string.digits)
    # First, get the sizes available for this product
    sizes = getSizes()
    # Find all of the color inputs in the current window
    colorInputs = SpS.xpaths('//input[@name="Color"]')
    # Set up an list to hold all of the current colors
    currentColors = []
    # Add each current color to the list
    for c in colorInputs:
        if c['value'] not in currentColors:
            currentColors.append(c['value'])
    # Gather all of the update's skus
    # TODO: Modify this, these specific valid SKUs are only relevant to Southern Tide items atm
    # TODO: Check this new modification, completed but needs testing with other products/brands
    # First, create an list
    validSKUs = []
    # Create another list consisting of the lengths of each respective sku
    lens = [len(sks) for sks in jda[name]['skus']]
    # Get the total number of colors in the item
    cl = len(jda[name]['colors']) - len(sizes)
    # Initialize the length of each color's sku
    color_len = 0
    # Find the length of the skus that each match up to a color (1-to-1 ratio between color and skus)
    for l in lens:
        if lens.count(l) == cl:
            color_len = l
            break
    # Append the valid skus to the list of valid skus
    for sks in jda[name]['skus']:
        if len(sks) == color_len:
            validSKUs.append(sks)
    # Likewise, find all of the current SKU inputs
    skuInputs = SpS.xpaths('//input[@name="sku"]')
    # Set up an list to hold all current SKUs
    currentSKUs = []
    # Add each current SKU to the list
    for s in skuInputs:
        # Get the current referenced sku by parsing using the string class
        # First, save the current value
        currentValue = s['value']
        # Translate the parsed SKU
        # currentValue = currentValue.translate(nodigs)
        currentValue = currentValue[:5]
        # Use the parsed SKU and save it to the current SKU list
        if currentValue not in currentSKUs:
            currentSKUs.append(currentValue)
    # Go through each of the new colors
    for c in colors:
        # If there is a color in the new data that is not in the old data, start the process of adding it
        if c not in currentColors and len(currentSKUs) != 0:
            # Now we need the proper SKU number for this color
            sharedIndex = jda[str(name)]['colors'].index(c)
            try:
                colorSKU = currentSKUs[sharedIndex]
            except:
                sharedIndex = 0
                colorSKU = currentSKUs[0]
            # Check to make sure that this sku doesn't already exist, and if it does, find the correct one from the list
            # Limit the number of times this repeats to the length of the new sku list
            repititions = 0
            while colorSKU[:5] in currentSKUs and repititions < len(validSKUs):
                # If it hits the end of the list, loop around
                if sharedIndex == len(validSKUs) - 1:
                    sharedIndex = 0
                # Otherwise just increment the reference index
                else:
                    sharedIndex = sharedIndex + 1
                # Update the SKU and the number of repititions that has been completed
                colorSKU = validSKUs[sharedIndex]
                repititions += 1
            currentSKUs.append(colorSKU)
            ### NOTE: Even though it doesn't look like it, changing the queries is not necessary since new options are being made ###
            # Check to ensure the right tab is open
            '''tab_text = browser.find_by_xpath('//a[contains(@class, "configuration-container-tab active")]')[0].text
            # If it isn't, make it so
            if tab_text != 'Pricing & Variants':
                # Python used Pound!
                try:
                    browser.find_by_xpath('//a[contains(@class, "configuration-container-tab")]')[1].click()
                except:
                    action = ActionChains(browser.driver)
                    SpS.move_to(browser.find_by_xpath('//a[contains(@class, "configuration-container-tab")]')[1])
                    action.click()
                    action.perform()'''
            
            # Loop through each of the possible sizes and work accordingly
            for s in sizes:
                # First, find and hit the "Add Variant" Button
                addVariant = browser.find_by_css('div.add-variant')
                try:
                    # Python used Pound!
                    addVariant.click()
                except:
                    try:
                        # Find the "Add Variant" button using the selenium driver
                        addVariant = browser.driver.find_element_by_css_selector('div.add-variant')
                        # Python used Pound!
                        addVariant.click()
                    except:
                        # Python used Teleport!
                        SpS.runScript('return arguments[0].scrollIntoView();', addVariant)
                        # Python used Rest!
                        SyS.slp3()
                        # Python used Pound!
                        print(name)
                        addVariant.click()
                # Find the SKU input
                sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                # Try to click
                try:
                    # Python used Pound!
                    sku.click()
                # If that stupid pop-up rears its ugly cranium, click the button to get rid of it
                except exceptions.WebDriverException:
                    confirmButton = SpS.css('.confirmation-button.no-frame.confirm')
                    # Python used Rest!
                    SyS.slp3()
                    # Python used Pound!
                    confirmButton.click()
                    # Python used Rest!
                    SyS.slp3()
                    # Python used Pound!
                    sku.click()
                # Python used Rest!
                SyS.slp3()
                # Get the current skus in the list
                c_skus = get_skus()
                c_sku = colorSKU + s
                counter = 1
                while c_sku in c_skus:
                    c_sku = c_sku[:len(colorSKU)] + str(counter) + c_sku[-len(s):]
                    counter += 1
                # Use the current size for this color to determine and enter the SKU
                sku.type(c_sku)
                # Now to enter the actual color
                colorIn = SpS.css('div.rows>div:last-of-type div.attribute[name="Color"] input')
                # Python used Pound!
                colorIn.click()
                # Python used Rest!
                SyS.slp3()
                colorIn.type(c)
                # And finally the size
                size = SpS.css('div.rows>div:last-of-type div.attribute:last-of-type input')
                # Python used Pound!
                size.click()
                size.type(s)
            # If no sizes are used, this still needs adding, so handle that here
            if len(sizes) == 0:
                # First, find and hit the "Add Variant" Button
                addVariant = browser.find_by_css('div.add-variant')
                try:
                    # Python used Pound!
                    addVariant.click()
                except:
                    # Python used Teleport!
                    SpS.runScript('return arguments[0].scrollIntoView();', addVariant)
                    # Python used Pound!
                    addVariant.click()
                # Find the SKU input
                sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                # Try to click
                try:
                    # Python used Pound!
                    sku.click()
                # If that stupid pop-up rears its ugly cranium, click the button to get rid of it
                except exceptions.WebDriverException:
                    confirmButton = SpS.css('.confirmation-button.no-frame.confirm')
                    # Python used Rest!
                    SyS.slp3()
                    # Python used Pound!
                    confirmButton.click()
                    # Python used Rest!
                    SyS.slp3()
                    # Python used Pound!
                    sku.click()
                # Python used Rest!
                SyS.slp3()
                c_skus = get_skus()
                counter = 1
                while colorSKU in c_skus:
                    colorSKU = (colorSKU if counter == 1 else colorSKU[:-len(str(counter - 1))]) + str(counter)
                # Use the current size for this color to determine and enter the SKU
                sku.type(colorSKU)
                # Now to enter the actual color
                colorIn = SpS.css('div.rows>div:last-of-type div.attribute[name="Color"] input')
                # Python used Pound!
                colorIn.click()
                # Python used Rest!
                SyS.slp3()
                # Type in the color
                colorIn.type(c)


### Note: The below two methods only work with size-less items, or specific items like Skipjack Polo ###
# Checks the order the colors of an item are currently stored as
def check_color_order():
    # Get the rows of colors
    rows = browser.driver.find_elements_by_css_selector('div.sqs-variant-row-content>div.variant-row')
    # Create a list for the current order of the rows
    current_order = []
    # For each row
    for r in rows:
        # Append the colors in order to the list
        current_order.append(
            SpS.Xpath(r, '/div[@class="attributes"]/div[@name="Color"]//input[@name="Color"]').get_attribute('value'))
    # Return the current order the colors are stored in
    return rows, current_order


# Re-arranges the colors of an item to match the latest pictures uploaded, now works with all items, size or not
def re_arrange_colors(name):
    # Get the current order the colors are stored in
    rows, current_order = check_color_order()
    # Store the order they need to be in
    needed_order = jda[name]['colors']
    # Create the array to indicate where each element needs to move
    movement_needed = []
    # Figure out what needs moving and the index each one needs to move to
    for i in range(len(current_order)):
        try:
            movement_needed.append(needed_order.index(current_order[i]))
        except:
            pass
    # Create the ActionChains object to move these items around with
    action_chains = ActionChains(browser.driver)
    # If movement is in fact needed
    if len(movement_needed) != 0:
        # Loop through each position
        for i in range(max(movement_needed) + 1):
            try:
                # Move the first element of the current index to that location
                action_chains.move_to_element_with_offset(rows[movement_needed.index(i)], 200,
                                                          0).click_and_hold().pause(
                    0.5).move_to_element(rows[i]).release().perform()
                # Reset the action_chains variable
                action_chains.reset_actions()
                # Refresh the rows and the current order of the colors
                rows, current_order = check_color_order()
                # Re-initialize the movement needed
                movement_needed = []
                # Re-populate the movement needed
                for i in range(len(current_order)):
                    movement_needed.append(needed_order.index(current_order[i]))
            except:
                pass
    # action_chains.move_to_element(browser.driver.find_element_by_css_selector('input.saveAndClose')).perform()


# Updates the colors as necessary (Confirmed)
def updateColors(name, colorInfo):
    # Get the information for the colors
    oldColors = colorInfo['oldInfo']
    newColors = colorInfo['newInfo']
    # Delete old colors
    deleteColors(oldColors)
    # Add new colors
    addColors(name, newColors)
    # Re-arranges the colors left to match the order of the images
    re_arrange_colors(name)


# Update price (Confirmed) TODO: Add sale price handling
def updatePrice(name):
    # Get the new price
    newPrice = jda[name]['price']
    # Find all of the price inputs
    prices = list(SpS.csss('div.sqs-pricing-input-content'))
    # Create a variable to keep track of location
    current = 0
    # For each of the inputs
    for p in prices:
        # Try just clicking the element
        try:
            # Python used Pound!
            p.click()
        # If it can't be clicked
        except:
            # It wasn't very effective...
            # Try running a script to scroll to that element, then Python used Pound!
            try:
                # Executing script
                SpS.runScript("return arguments[0].scrollIntoView();", p)
                # Python used Pound!
                p.click()
            # If that doesn't work, re-create the original list and use that to do what's needed
            except:
                # It wasn't very effective...
                p = SpS.csss('div.sqs-pricing-input-content')[current]
                SpS.runScript("return arguments[0].scrollIntoView();", p)
                # Python used Pound!
                p.click()
        # Switch to the active element that is generated, and first hit backspace and the new price
        browser.driver.switch_to_active_element().send_keys(Keys.BACK_SPACE + newPrice)
        # Then wait a moment and hit Enter
        # Python used Rest!
        SyS.slp(0.1)
        browser.driver.switch_to_active_element().send_keys(Keys.ENTER)
        # Increment the current position just in case of errors
        current = current + 1
        # Python used Rest!
        SyS.slp3()


# Updates stocks during the process of updating an item (Only works when second page is active)
def updateStocks(name):
    # Grab the global json data
    global jda
    # Grab the color data of the given item
    cd = jda[name]['color_data']
    # Find all of the text inputs for the stocks
    stock_ins = SpS.xpath('//div[@class="sqs-stock-input-content"]')
    # Grab the current colors and sizes stored in the order in which they appear
    color_ins = SpS.xpath('//div[@name="Color"]//input')
    size_ins = SpS.xpath('//div[@name="Size"]//input')
    # Create and populate a list of all the item's colors in the order they appear
    colors_in_order = []
    for i in range(len(color_ins)):
        colors_in_order.append(color_ins[i]['value'])
    in_order = True
    seen = []
    # Determine whether or not this list has been sorted (and thus order is wonky)
    # This may not be necessary, but will leave it in just in case things go wrong
    for i in range(len(colors_in_order)):
        if colors_in_order[i] not in seen:
            seen.append(colors_in_order[i])
        else:
            if colors_in_order[i-1] == colors_in_order[i]:
                continue
            else:
                in_order = False
                break
    for i in range(len(stock_ins)):
        if stock_ins[i].text == '0' and size_ins[i]['value'] in cd[colors_in_order[i]]:
            # Click the stock to bring up the pop-up
            stock_ins[i].click()
            # Check the box to mark unlimited stock
            qty = WebDriverWait(browser.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
            # Python used Pound!
            try:
                qty.click()
            except:
                SyS.slp(1)
                qty = WebDriverWait(browser.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
                try:
                    qty.click()
                except:
                    SpS.move_and_click(qty)
        elif stock_ins[i].text != '0' and size_ins[i]['value'] not in cd[colors_in_order[i]]:
            # Click the stock to bring up the pop-up
            stock_ins[i].click()
            # Check the box to mark unlimited stock
            qty = WebDriverWait(browser.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
            # Python used Pound!
            try:
                qty.click()
            except:
                SyS.slp(1)
                qty = WebDriverWait(browser.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
                qty.click()
            # Python used Rest!
            SyS.slp(1)
            # Type a zero into the stock value
            browser.find_by_xpath('//input[@name="qtyInStock"]')[0].type('0')

# Updates SKUs
# Deprecated for right now, treating skus + sizes as base references
def updateSKUs(name):
    newSKUs = jda[name]['skus']
    logging.debug(newSKUs)


# Stock handling method, includes limited to unlimited conversion
def updateStock(stock_updates, now_limited=None):
    # Python used Iterate!
    for k in stock_updates:
        # Python used Pound!
        SpS.select_item(SpS.item_name(k))
        # Get the variants tab
        variants_tab = []
        # Create a repetitions count var
        current = 0
        # While either there are still repetitions to go or the tab hasn't been found yet
        while len(variants_tab) == 0 and current < 60:
            # Try getting the tab
            try:
                variants_tab = SpS.xpath('//div[contains(text(), "Variants")]')
            # Otherwise just forget about it
            except:
                pass
            # Python used Rest!
            SyS.slp(.1)
            # Increment the repetitions counter
            current += 1
        # Python used Pound!
        SpS.move_and_click(variants_tab)
        # Find all of the text inputs for the stocks
        stock_inputs = SpS.xpath('//div[@class="sqs-stock-input-content"]')
        # Loop through each input
        for i in range(len(stock_inputs)):
            # Python used Rest!
            SyS.slp2()
            # Python used Pound!
            stock_inputs[i].click()
            # Create the current value var
            cv = None
            if type(stock_updates[k]) is dict:
                # Get the current key
                ck = list(stock_updates[k].keys())[i]
                # Get the current stock value
                cv = stock_updates[k][ck]
            else:
                # Get the key associated with this item (probably refers to making a current unlimited item limited)
                cv = stock_updates[k]
            # If the value has changed and isn't changing to unlimited
            if browser.find_by_xpath('//input[@name="qtyInStock"]')[0]['value'] != cv and cv != -1:
                if now_limited is not None and k in now_limited:
                    # Find the text for the label
                    unlimited_label = browser.find_by_text('Unlimited')[0]
                    # Python used Pound!
                    unlimited_label.click()
                    # Python used Rest!
                    SyS.slp(1)
                try:
                    # Find the input label and handle appropriately
                    browser.find_by_xpath('//input[@name="qtyInStock"]')[0].type(str(cv))
                except:
                    # Find the text for the label
                    unlimited_label = browser.find_by_text('Unlimited')[0]
                    # Python used Pound!
                    unlimited_label.click()
                    # Python used Rest!
                    SyS.slp(1)
                    # Find the input label and handle appropriately
                    browser.find_by_xpath('//input[@name="qtyInStock"]')[0].type(str(cv))
            # Otherwise if it has changed and is changing to unlimited
            elif browser.find_by_xpath('//input[@name="qtyInStock"]')[0]['value'] != cv and cv == -1:
                # Find the text for the label
                unlimited_label = browser.find_by_text('Unlimited')[0]
                # Python used Pound!
                unlimited_label.click()
            # Python used Pound!
            SpS.move_and_click(variants_tab)
            # Python used Rest!
            SyS.slp2()
        # After the stocks have been updated properly, find the save button
        try:
            save_button = SpS.val('Save')[0]
        except:
            SyS.slp(3)
            save_button = SpS.val('Save')[0]
        # Python used Pound!
        save_button.click()
        # Python used Rest!
        SyS.slp2()


# endregion

### Moving Items Around ###
# region Moving Items
# Moves an item to a different page based on previous season
def moveItemFromStore(name):
    # Find and click the item we want to move
    # Python used Pound!
    SpS.move_and_click(SpS.item_name(name))
    # Find the now visible move button
    currentMovedItem = SpS.xpath('//div[@class="product-grid-action-tray"]/div[@class="buttons"]/div[@title="Move"]')
    # Python used Pound!
    SpS.move_and_click(currentMovedItem)
    # Python used Rest!
    SyS.slp(1)
    # Get information for where to store this stuff
    currentSeason = get_season(date.today())
    currentYear = datetime.now().year
    # Try getting the other page of the current year which should be the only option that shows up with that year)
    try:
        page = SpS.xpath(
            '//div[@class="collection-group"]/div[contains(@data-url-id, "' + currentSeason.lower() + "-" + str(
                currentYear) + '")]//span')
    # If that doesn't work out (i.e. Spring of each year), send it to one from the last year
    except:
        # Find the previous season (Assume Fall if Spring/Summer, Spring if Fall/Winter)
        if currentSeason == 'Fall' or currentSeason == 'Winter':
            currentSeason = 'Spring'
        else:
            currentSeason = 'Fall'
        # Try to set it to a previous year
        try:
            page = SpS.xpath(
                '//div[@class="collection-group"]/div[contains(@data-url-id, "' + currentSeason.lower() + "-" + str(
                    currentYear - 1) + '")]//span')
        # If that doesn't work, just forget this time
        except:
            page = None
    # If we actually have something, confirm the move
    if page is not None:
        # Select the page to move it to
        page.click()
        # Find the move button
        moveItemButton = SpS.xpath('//input[@value="Move Item"]')
        # Python used Pound!
        moveItemButton.click()
        # Python used Rest!
        SyS.slp(1.5)
    else:
        logging.debug('Something went wrong')


# Moves a set of given items from the store
def moveItemsFromStore(oldItems):
    # Create a new ActionChain
    action = ActionChains(browser.driver)
    # Begin holding the control button down
    action.key_down(Keys.CONTROL)
    # For each item given
    for o in oldItems:
        # Move to the element and click it
        action.move_to_element(SpS.item_name(o))
        # Python used Rest!
        SyS.slp2()
        # Python used Pound!
        action.click()
        # Python used Rest!
        SyS.slp2()
    # Release control
    action.key_up(Keys.CONTROL)
    # Perform the action
    action.perform()
    # Python used Rest!
    SyS.slp(2)
    # Find the now visible move button
    currentMovedItem = SpS.xpath('//div[@class="product-grid-action-tray"]/div[@class="buttons"]/div[@title="Move"]')
    # Python used Pound!
    SpS.move_and_click(currentMovedItem)
    # Python used Rest!
    SyS.slp(1)
    # Get information for where to store this stuff
    currentSeason = get_season(date.today())
    currentYear = datetime.now().year
    # Try getting the other page of the current year which should be the only option that shows up with that year)
    try:
        page = SpS.xpath(
            '//div[@class="collection-group"]/div[contains(@data-url-id, "' + currentSeason.lower() + "-" + str(
                currentYear) + '")]//span')
    # If that doesn't work out (i.e. Spring of each year), send it to one from the last year
    except:
        # Find the previous season (Assume Fall if Spring/Summer, Spring if Fall/Winter)
        if currentSeason == 'Fall' or currentSeason == 'Winter':
            currentSeason = 'Spring'
        else:
            currentSeason = 'Fall'
        # Try to set it to a previous year
        try:
            page = SpS.xpath(
                '//div[@class="collection-group"]/div[contains(@data-url-id, "' + currentSeason.lower() + "-" + str(
                    currentYear - 1) + '")]//span')
        # If that doesn't work, just forget this time
        except:
            page = None
    # If we actually have something, confirm the move
    if page is not None:
        # Select the page to move it to
        page.click()
        # Find the move button
        moveItemButton = SpS.xpath('//input[@value="Move Items"]')
        # Python used Pound!
        moveItemButton.click()
        # Python used Rest!
        SyS.slp(1.5)
    else:
        logging.debug('Something went wrong')


# Moves an item from a different page to the main store page
def moveItemToStore(name):
    # Find and click the item we want to move
    # Python used Pound!
    SpS.move_and_click(SpS.item_name(name))
    # Find the now visible move button
    currentMovedItem = SpS.xpath('//div[@class="product-grid-action-tray"]/div[@class="buttons"]/div[@title="Move"]')
    # Python used Pound!
    SpS.move_and_click(currentMovedItem)
    # Python used Rest!
    SyS.slp(1)
    # Attempt to click the store page link
    try:
        page = SpS.xpath('//div[@class="collection-group"]/div[@data-url-id="shop"]//span')
    # If that doesn't work out, don't even try
    except:
        page = None
    # If we actually have something, confirm the move
    if page is not None:
        # Select the page to move it to
        page.click()
        # Find the move button
        moveItemButton = SpS.xpath('//input[@value="Move Item"]')
        # Python used Pound!
        moveItemButton.click()
        # Python used Rest!
        SyS.slp(1.5)
    else:
        logging.debug('Something went wrong')


def moveItemsToStore(items):
    # Find and click the items we want to move
    # Create an ActionChain
    action = ActionChains(browser.driver)
    # Hold down Ctrl
    action.key_down(Keys.CONTROL)
    # For each item given
    for i in items:
        # Move to the element
        action.move_to_element(SpS.item_name(i))
        # Python used Rest!
        SyS.slp2()
        # Python used pound!
        action.click()
    # Release Ctrl
    action.key_up(Keys.CONTROL)
    # Perform the action
    action.perform()
    # Python used Rest!
    SyS.slp(2)
    # Find the now visible move button
    currentMovedItem = SpS.xpath('//div[@class="product-grid-action-tray"]/div[@class="buttons"]/div[@title="Move"]')
    # Python used Pound!
    SpS.move_and_click(currentMovedItem)
    # Python used Rest!
    SyS.slp(2)
    # Attempt to click the store page link
    try:
        page = SpS.xpath('//div[@class="collection-group"]/div[@data-url-id="shop"]//span')
    # If that doesn't work out, don't even try
    except:
        page = None
    # If we actually have something, confirm the move
    if page is not None:
        # Select the page to move it to
        page.click()
        # Find the move button
        moveItemButton = SpS.xpath('//input[@value="Move Item"]')
        # Python used Pound!
        moveItemButton.click()
        # Python used Rest!
        SyS.slp(1.5)
    else:
        logging.debug('Something went wrong')


# endregion

# endregion

# ------------------ END UPDATE METHODS ---------------------

# ---------------- BEGIN PROGRAM METHODS --------------------

# region Program

### Precursor comparison method ###
# Method to compare all data on the website with the new data
# Interesting discovery: this method has absolutely no usage of the browser, and thus can be done without activating selenium at all
# Parameters: infoToUpdate given data input, given as follows:
# If only one parameter is given, it's the url/indicator
# If there are two parameters, the first is given data, the second is the url/indicator of the page to compare
def compare_before(*infoToUpdate):
    # Comparison/Startup
    # As setup, get json data of all items from the store so that we don't have to use selenium for current data
    # First, check if there are 2+ parameters given, and get the given data if necessary
    global jda, jdn, Item, new_names, origins
    if len(infoToUpdate) > 1:
        # Set update data
        jda = infoToUpdate[0]
    # If one or no parameters or given
    else:
        # Create Conversion instance
        c = Conversion()
        # Get the json data
        jda = c.convert('items.json')
    
    # Initialize set up the namedtuple class and instance
    Item = namedtuple('Item', list(jda[list(jda.keys())[0]].keys()))
    for k in jda:
        jdn[k] = Item._make([jda[k][k1] for k1 in jda[k]])
    
    # Due to problems with colors and pictures not matching, eliminate all blank colors from jda here, and store all names
    for n in jda:
        # Storing names
        new_names.append(n)
        # Removing blank colors
        if jda[n]['colors'] is not None:
            for color in jda[n]['colors']:
                try:
                    if str(color) == '':
                        jda[n]['colors'].remove(color)
                except:
                    pass
    
    # Create the list for the store pages
    store_pages = []
    # Opening the file to read it
    with open('information.py') as f:
        for l in f.readlines():
            # If the current line is a store page
            if 'STORE_PAGE' in l or 'INVENTORY_PAGE' in l:
                # Append it to the list
                store_pages.append(l)
    # Remove the first entry (it's a comment)
    store_pages = store_pages[1:]
    # Create a list of page variable names
    store_page_names = []
    # And populate it
    for s in store_pages:
        store_page_names.append(s.split(' = ')[0].strip())
    # Convert each variable name to its url equivalent
    store_page_urls = []
    for s in store_pages:
        # If it's the store page variable, it's the base shop
        if s == 'STORE_PAGE':
            store_page_urls.append('shop')
        # If it's the second, then it's the second shop
        elif s == 'INVENTORY_PAGE':
            store_page_urls.append('shop-more')
        # If it's a season shop
        elif 'INVENTORY_PAGE_' in s:
            store_page_urls.append('shop-' + s[15:].replace('_', '-').lower())
        # If it's a shop with a number
        else:  # if 'STORE_PAGE_' in s
            store_page_urls.append('shop-' + s[11:])
    # Get url for the current data from the given keywords/url
    url = 'https://www.lionelsmithltd.com/shop?format=json'
    
    # Shorter version of earlier code to allow for more speed and reliability
    # Set ifj to a place in the memory
    ifj = {}
    # Try a maximum of 20 times
    maxTries = 250
    # Create a counter
    current = 0
    # While either ifj is still not filled or the maximum tries have no been attempted
    while ifj == {} and current < maxTries:
        # Try to parse the json from the given url
        try:
            ifj = json.loads(urllib.request.urlopen(url).read())['items']
        # If that doesn't work, increase the current counter
        except:
            # It wasn't very effective...
            current = current + 1
    # For each store page urls
    '''for s in store_page_urls:
        # Create the url from the current variable
        current_url_str = 'https://www.lionelsmithltd.com/' + s + '?format=json'
        # Provided that it's not the url used to create ifj
        if current_url_str != url:
            # Reset current
            current = 0
            # Create a variable for the new json data
            current_data = None
            # Using the same criteria as before
            while current_data is None and current < maxTries:
                # Try getting the json data
                try:
                    current_data = json.loads(urllib.urlopen(current_url_str).read())['items']
                except:
                    current = current + 1
            # Try to
            try:
                # take each entry in the data
                for c in current_data:
                    # and if it's not already there
                    if c not in ifj:
                        # add it to ifj
                        ifj.append(c)
            # Otherwise do nothing
            except:
                pass'''
    # Final variable to be used later
    jFinal = {}
    # Individual components assembled from the ifj list/JSON
    # If loop placed here to allow copy and pasting into console for testing easier (indents ugh), copy starting at the if
    # if True:
    inames = []
    idesc = []
    idetails = []
    icolors = []
    iprices = []
    iimgs = []
    itags = []
    iskus = []
    
    # Construct the total list of origin stores
    for a in jda:
        if jda[a]['origin'] not in origins:
            origins.append(jda[a]['origin'])
    # Remove unnecessary tags and other info to allow for more direct info comparisons
    # ----------------- BEGIN FOR -------------------
    for i in ifj:
        # Base Description
        # Get the description
        tempDesc = i['excerpt']
        # Take out the fluff
        tempDesc = tempDesc.replace('<p>', '')
        tempDesc = tempDesc.replace('</p>', '')
        # Append it to the descriptions
        idesc.append(tempDesc)
        
        # Details
        # Get the body
        tempBody = i['body']
        # Get everything needed
        listItems = re.findall(r'<li>(?P<inner_desc>.*?)</li>', tempBody)
        # If nothing was found, try a different search
        if len(listItems) == 0:
            listItems = re.findall(r'<p>-\s(?P<inner_desc>.*?)</p>', tempBody)
        # Append it to the details
        idetails.append(listItems)
        
        # Tags
        # Append the tags
        try:
            itags.append(i['tags'])
        except:
            pass
        
        # Name
        # Get the name
        tempName = i['title']
        # Take out the origin store text
        for o in origins:
            # By checking if the store is in the name
            if o in tempName:
                # And removing it
                tempName = tempName.replace(o + ' ', '')
                break
        # Append the name
        inames.append(tempName)
        
        # Colors and Prices (Inside JSON product variants)
        # Set up temporary variables
        tempColors = []
        tempSkus = []
        first = True
        # Go through each variant
        for v in i['variants']:
            # Colors
            # If the color isn't included already
            ### Note that originally 'optionValues' was u'optionValues', putting this here in case something goes wrong later ###
            try:
                if v['optionValues'][0]['value'] not in tempColors:
                    # Add the color to the temp
                    tempColors.append(v['optionValues'][0]['value'])
                    # Add the SKU to the temp
                    tempSkus.append(v['sku'])
            except:
                tempSkus.append(v['sku'])
            # Price
            # Only run for the first time around
            if first:
                # Append the price
                iprices.append(float(float(v['price']) / 100.0))  # Confirmed
                # Indicate not to run this any more
                first = False
        # Append the SKUs
        iskus.append(tempSkus)
        # Append the colors
        icolors.append(tempColors)
        
        # Imgs
        # Create somewhere to keep the images
        tempImgs = []
        # Go through each image
        for img in i['items']:
            # Take just the file name
            tempImgs.append(img['assetUrl'].split('/')[-1])
        # Append the image name
        iimgs.append(tempImgs)
    pass  # Placed so console doesn't freak out about indentation issues
    # ------------------ END FOR --------------------
    
    # Compile it all together
    for n in inames:
        # Find the current index
        current = inames.index(n)
        # Set the default of the current data entries
        noPrintJ = jFinal.setdefault(n, {'desc': '', 'dets': [], 'tags': [], 'colors': [], 'imgs': [], 'price': '',
                                         'skus': []})
        # noPrintR = relItems.setdefault(n, {'desc':'', 'dets': [], 'tags': [], 'colors': [], 'imgs': [], 'price': '', 'skus': []})
        # Set the jFinal entries
        jFinal[n]['desc'] = idesc[current]
        jFinal[n]['dets'] = idetails[current]
        try:
            jFinal[n]['tags'] = itags[current]
        except:
            jFinal[n]['tags'] = []
        jFinal[n]['colors'] = icolors[current]
        jFinal[n]['price'] = iprices[current]
        jFinal[n]['imgs'] = iimgs[current]
        jFinal[n]['skus'] = iskus[current]
        # set the relItems entries
        # relItems[n]['desc'] = idesc[current]
        # relItems[n]['dets'] = idetails[current]
        # relItems[n]['tags'] = itags[current]
        # relItems[n]['colors'] = icolors[current]
        # relItems[n]['price'] = iprices[current]
        # relItems[n]['imgs'] = iimgs[current]
        # relItems[n]['skus'] = iskus[current]
    # logging.debug(jFinal)
    # Begin the process of comparing old data with new data
    # Version 0.1 (current) only update existing items
    # Version 0.2 (future and hopefully final product) add non-existing items
    
    # Create a variable to hold a truth table of what to update and what not to update
    updatesNeeded = {}
    
    # ---------------- BEGIN FOR ----------------
    
    # Iterate each index of jda
    for item in jda:
        # ----- START IF -----
        # If the name of the updated item is in the old list, then continue
        if item in jFinal:
            # Save current item object to make things easier to reference and shorter in the long run
            currentItem = jda[item]
            
            # Save the common name for easier reference
            currentName = item
            logging.debug(currentName)
            
            # Set the default of the current entry in our truth table
            # Variable is used to keep the empty dict from printing every time.
            # Experimental: Adding an indicator for the difference in removing old images and adding new ones
            randomThingToKeepFromPrinting = updatesNeeded.setdefault(currentName,
                                                                     {
                                                                         'description': False,
                                                                         'dets': False,
                                                                         'tags': False,
                                                                         'colors': {'oldInfo': [], 'newInfo': []},
                                                                         'imgs': False,
                                                                         'old_imgs': False,
                                                                         'new_imgs': [],
                                                                         'price': False,
                                                                         'skus': False
                                                                     })
            # Every. Single. Time.
            randomThingToKeepFromPrinting['description'] = False
            
            # First, check the one-line data fields
            # Check the description
            # New Description with first-person translated to third-person (maybe 4th?)
            woST = SyS.other_people(currentItem['description'], currentItem['origin'])
            # compareDesc = SyS.other_people(jFinal[currentName]['desc'].replace("&nbsp;", ""), currentItem['origin'])
            
            ### Originally the note about bad coding practice was here, but after adding above   #
            #                        compareDesc variable, efficiency has drastically improved ###
            
            # Compare the old and new data
            try:
                # if (compareDesc.strip() != woST.strip() and woST.strip() != '') or currentItem['description'].strip() == '':
                #    # Print our original, and then their new entry (with the appropriate substitutions)
                #    logging.debug('Ours:   '+ compareDesc + '\nTheirs:' +woST)
                #    logging.debug('Desc Correction needed')
                #    updatesNeeded[currentName]['desc'] = True
                # else:
                #    logging.debug('Description is fine')
                
                # Check the price
                ### Note that '$' used to be u'$', putting this here just in case something goes wrong later ###
                if '$' + '%.2f' % jFinal[currentName]['price'] != currentItem['price']:
                    logging.debug(
                        'The price is not right')  # Dev high-fives himself while users groan in agony from what should be regarded as a great joke
                    updatesNeeded[currentName]['price'] = True
                
                # Next, check the lists for validity, by seeing if the old list is inside the other and if both are the same length
                # Before we do that, we need to handle the extra character that comes from the scraper seemingly at random
                # tempDets = []
                # tempDets1 = []
                # Handle that weird character
                # for l in jFinal[currentName]['dets']:
                #    tempDets1.append(l.replace('&nbsp;',  ' ').replace('&amp;','&'))
                # weirdness = re.compile('\\xa0')
                
                # Create the new list to deal with
                # for lI in currentItem['details']:
                #    tempDets.append(weirdness.sub(' ', lI))
                
                # Check details list
                # if not SyS.compare(tempDets1, tempDets):
                #    logging.debug(str(tempDets1) + ' ' + str(tempDets))
                #    logging.debug('Details Correction needed')
                #    updatesNeeded[currentName]['dets'] = True
                # else:
                #    logging.debug('Details are fine')
                
                # Check basic imgs list, confirming the need for image updates
                if SyS.compare_imgs(jFinal[currentName]['imgs'], currentItem['images']):
                    logging.debug(jFinal[currentName]['imgs'] + 'str' + currentItem['images'])
                    updatesNeeded[currentName]['imgs'] = True
                
                # Check the colors and variants (this is the long one)
                # First, check the old colors compared to the new ones, and mark the old ones for removal
                for color in jFinal[currentName]['colors']:
                    if color not in currentItem['colors']:
                        logging.debug(color + ' no longer sold, remove this option')
                        # Append this color to the ones being deleted
                        updatesNeeded[currentName]['colors']['oldInfo'].append(color)
                        # Indicate the specific need to take out old pictures
                        updatesNeeded[currentName]['old_imgs'] = True
                
                # Create an list to hold the original colors without changing the original data
                tempCurrentColors = []
                
                # Remove any size info from the data
                for color2 in currentItem['colors']:
                    # First check for letter sizes, and then for number sizes
                    if (color2 != 'XXS' and color2 != 'XS' and color2 != 'S' and color2 != 'M' and color2 != 'L'
                            and color2 != 'XL' and color2 != 'XXL' and color2 != 'XXXL'
                            and not str(color2).isdigit()):
                        tempCurrentColors.append(color2)
                
                # Now for each of the new colors, if it's not there, mark it for upload
                for color3 in tempCurrentColors:
                    if color3 not in jFinal[currentName]['colors']:
                        if len(color3) != 0:
                            # First, indicate the addition of the color
                            logging.debug(str(color3) + 'not found, needs to be added')
                            updatesNeeded[currentName]['colors']['newInfo'].append(color3)
                            # Get the index of the current color
                            colorIndex = tempCurrentColors.index(color3)
                            # Find the corresponding color because their indexes <em>should</em> match
                            colorImageNeeded = currentItem['image_paths'][colorIndex]
                            # Attach the found url
                            updatesNeeded[currentName]['new_imgs'].append(colorImageNeeded)
                
                # logging.debug(updatesNeeded[currentName])
                logging.debug('')
            except:
                pass
        # ------ END IF ------
        else:
            # Add this variable into the updates needed packet so that we know it needs adding/moving
            # Note that each update variable is currently set to False
            # Variable is used to keep the empty dict from printing every time.
            randomThingToKeepFromPrinting = updatesNeeded.setdefault(item,
                                                                     {
                                                                         'description': False,
                                                                         'dets': False,
                                                                         'tags': False,
                                                                         'colors': {'oldInfo': [], 'newInfo': []},
                                                                         'imgs': False,
                                                                         'old_imgs': False,
                                                                         'new_imgs': [],
                                                                         'price': False,
                                                                         'skus': False
                                                                     })
            # Every. Single. Time.
            randomThingToKeepFromPrinting['description'] = False
    # ----------------- END FOR -----------------
    
    # With all of the information parsed, compared, and validified, call the next method to being the process of updating the data
    # updateAfter(updatesNeeded)
    return updatesNeeded


### End Precursor Comparison Method ###

# Method for testing pure store updates without adding items or moving them around
def update_store(updatesNeeded, *possible_data):
    ### User Display ###
    # Displays a simple prompt so that no one works on the store until this is done
    
    ### Setup ###
    # Get the globals needed
    global all_names, new_names, jda
    # If necessary, we now begin the updating procedure
    # First, check to make sure we're not already on the right page
    # Get the url we'd be referencing
    # goingToUrl = get_admin_url(url)
    # If the two are equal, then just skip straight to the update process
    if browser.url == Info.STORE_PAGE:
        pass
    # Otherwise,
    else:
        # Step 1a: Accessing login page by direct link to store page
        # By default, it relates to the store page
        browser.visit(Info.STORE_PAGE)
    
    # Get the global loggedIn and check it
    global logged_in
    # If the program isn't already logged in, get that way
    if not logged_in:
        # Log in to the page using the previously defined method
        login()
    
    # Give the window some time to load
    # Python used Rest!
    SyS.slp(5)
    # Get the new list of items from this page
    productNames = SpS.get_item_names()
    oldProducts = []
    done = []
    
    # Check to see if jd data was sent with the method, and if so set this class's jda to the given data
    try:
        jda = possible_data[0]
    except:
        pass
    
    ### Updating ###
    # ---------------- BEGIN FOR ----------------
    # For every product located by name
    for n in productNames:
        currentUpdates = None
        replaced = ''
        try:
            # Create a variable for the updates that are indicated for this item
            currentUpdates = updatesNeeded[str(n).replace('Southern Tide ', '')]
            replaced = 'Southern Tide '
        except:
            try:
                currentUpdates = updatesNeeded[str(n).replace('Psycho Bunny ', '')]
                replaced = 'Psycho Bunny '
            except:
                try:
                    currentUpdates = updatesNeeded[str(n).replace('Saxx ', '')]
                    replaced = 'Saxx '
                except:
                    pass
        # If nothing was assigned, keep moving on
        if str(n).replace(replaced, '') not in updatesNeeded:
            oldProducts.append(n)
            # Python used Future Sight!
            continue
        # Before we start moving at all in the window, we first figure out where we need to go, since the data has already been observed in order to get here
        # To do this, we create a local, easy-to-read dict of booleans for our reference
        bools = {'desc': False, 'dets': False, 'tags': False, 'colors': False, 'imgs': currentUpdates['imgs'],
                 'old_imgs': False, 'new_imgs': [], 'price': False, 'skus': False}
        # Determine if colors need an update from the info given
        if len(currentUpdates['colors']['oldInfo']) > 0 or len(currentUpdates['colors']['newInfo']) > 0:
            bools['colors'] = True
            bools['imgs'] = True
        # Assign each variable to the currently needed updates for each field
        try:
            bools['desc'] = currentUpdates['desc']
        except:
            pass
        bools['dets'] = currentUpdates['dets']
        bools['tags'] = currentUpdates['tags']
        bools['price'] = currentUpdates['price']
        bools['skus'] = currentUpdates['skus']
        bools['old_imgs'] = currentUpdates['old_imgs']
        bools['new_imgs'] = currentUpdates['new_imgs']
        # Create a variable so that the program knows if the process has begun or not
        begun = False
        # Check if any of the variables are true
        for b in bools:
            # Try to use each one directly as a boolean
            try:
                # If any of them are true, begin the update process
                if bools[b]:
                    begun = update(n)
                    # Python used Brick Break!
                    break
            # If it's not a boolean, it's going to be an list
            except:
                # If there are some new images, begin the update process
                try:
                    if len(bools[b]) > 0:
                        begun = update(n)
                        # Python used Brick Break!
                        break
                # Breaking really weird right here for some reason, adding another exception to prevent that
                except:
                    if bools[b]:
                        begun = update(n)
                        break
        
        # ----- BEGIN IF -----
        # If the program detects an instantiated process, begin updating
        if begun:
            # Start checking each value to see if it needs updating, starting with the first screen that pops up
            # Check description
            if bools['desc']:
                try:
                    updateDesc(n.replace(replaced, ''))
                except:
                    pass
                # Python used Rest!
                SyS.slp3()
            # Check Tags
            updateTags(n)
            # Python used Rest!
            SyS.slp3()
            # Check Images
            if bools['imgs']:
                # First, we check to see if old images need removal, since it uses the old process
                if bools['old_imgs']:
                    updateImgs(n.replace(replaced, ''))
                # However, if the only operation needed is new image addition, go the shorter route
                elif len(bools['new_imgs']) > 0:
                    addImagesGiven(bools['new_imgs'])
                # Set the colors to True, just in case
                bools['colors'] = True
                # Python used Rest!
                SyS.slp(1.5)
            
            # Start checking second page stuff
            # TODO: Start unlimited stock checks here next time
            # If anything needs to be updated, find and click the next tab
            #if bools['price'] or bools['skus'] or bools['colors']:
            SpS.move_and_click(SpS.xpath('//div[contains(text(), "Pricing")]'))
            # Python used Rest!
            SyS.slp(1.5)
            # Check Price (since it's a universal in this case)
            # el
            if bools['price']:
                updatePrice(n.replace(replaced, ''))
            # Check SKUs
            if bools['skus']:
                updateSKUs(n.replace(replaced, ''))
            # Check Colors
            if bools['colors']:
                updateColors(n.replace(replaced, ''), currentUpdates['colors'])
                # Python used Rest!
                SyS.slp3()
            cn = generalize(n)
            if jda[cn]['origin'] not in inventory_dependents:
                updateStocks(n.replace(replaced, ''))
            # TODO: Actually continue here once update stocks method is completed
            # Finally, check the details and switch to that tab as well if necessary
            if bools['dets']:
                additionalTab = SpS.xpath('//div[contains(text(), "Additional")]')
                additionalTab.click()
                updateDetails(n.replace(replaced, ''))
                # Python used Rest!
                SyS.slp3()
            
            # Once completed, save and close the item
            SpS.save_and_close()
            SyS.slp(3)
        # ------ END IF ------
    # ----------------- END FOR -----------------
    print(str(len(productNames)) + ' items updated')
    # Below to hold folding in the right place
    pass


# Adds items based on the names given using the data given (mainly used from InventoryGui.py)
def add_new_items(newItemNames, *data_list):
    global marked
    # Create a counter to refresh the page every now and then
    counter = 0
    current_store_page = 1
    # Navigate to the page
    try:
        browser.visit(SyS.get_admin_url(data_list[1]))
    except:
        browser.visit(Info.STORE_PAGE)
    # Get the global loggedIn and check it
    global logged_in, new_names
    # If the program isn't already logged in, get that way
    if not logged_in:
        # Then log in
        login()
    ### Adding ###
    # Try getting the jd from the optional data given
    try:
        jd = data_list[0]
    # If that doesn't work out, just use the current jda
    except:
        jd = jda
    # Remove all blank stuff in the data
    for n in jd:
        if jd[n]['colors'] is not None:
            for color in jd[n]['colors']:
                if color is not None:
                    if str(color.encode('ascii', 'xmlcharrefreplace')) == '':
                        jd[n]['colors'].remove(color)
        if jd[n]['skus'] is not None:
            for sku in jd[n]['skus']:
                if sku is not None:
                    if str(sku.encode('ascii', 'xmlcharrefreplace')) == '':
                        jd[n]['skus'].remove(sku)
    # Then, figure out what's not already here
    # Python used Rest!
    SyS.slp(5)
    # Find all of the current items on the page
    current_items = SpS.get_item_names()
    # Create a variable representing how many items are on the page
    current_length = len(current_items)
    # Loop through the pages until it reaches a STORE_PAGE_x that has less than 200 items on it
    while current_length >= 200 and current_store_page < 25:
        # Python used Endeavor!
        try:
            # Increment the x in STORE_PAGE_x (assuming that we start x at 1)
            current_store_page += 1
            # Attempt to get the corresponding URL in the browser
            exec('browser.visit(Info.STORE_PAGE_' + current_store_page)
            SyS.slp(3)
            current_items = SpS.get_item_names()
            current_length = len(current_items)
        except:
            break

    # Create an list for new item names
    new_names = []
    # Loop through the given names and ensure they're not already there
    for n in newItemNames:
        if n not in current_items and n not in [generalize(c) for c in current_items]:
            new_names.append(n)
            
    # ======== Start For ==========
    # For each of the new items, we now start the adding process
    for n in new_names:
        # Before we actually begin adding the item, check to make sure there is room on the page
        # Note: should only trigger on equaling 200, but better safe than sorry
        if current_length >= 200:
            current_store_page += 1
            new_shop_page(current_store_page)
        # Variables needed for basic item classification
        global form_needed, fit_form_needed, pant_sizes, l_form_needed, unf_form_needed, widths
        form_needed = False
        # First, check to see what kind of item this is
        category = ''
        # Pants
        if 'Pant' in n or 'pant' in n:
            category = 'pants'
        # Python used Future Sight!
        # continue
        # Since short-sleeve shirts are in this, use shorts, not short
        elif 'shorts' in n or 'Shorts' in n:
            category = 'shorts'
        # Python used Future Sight!
        # continue
        # Parse out if there are shorts just referred to as "short" by comparing name
        elif ('short' in n or 'Short' in n) and ('sleeve' not in n or 'Sleeve' not in n):
            category = 'shorts'
        # Python used Future Sight!
        # continue
        # Blazers
        elif 'blazer' in n or 'Blazer' in n:
            category = 'blazer'
        # Python used Future Sight!
        # continue
        # Shirts
        elif 'shirt' in n or 'Shirt' in n or 'polo' in n or 'Polo' in n:
            category = 'shirt'
        # Unrelated swim items
        elif 'bikini' in n or 'Bikini' in n or 'Women' in n or 'women' in n:
            category = 'unrelated'
            # Python used Future Sight!
            continue
        # Other stuff
        else:
            category = 'misc'
        # This distinction will come in later, for now, begin new item process
        logging.debug(category)
        # Make sure the following variables are globals
        global shirt_sizes, shoe_sizes
        # Reset the variables
        removal = []
        shirt_sizes = []
        shoe_sizes = []
        widths = []
        n = generalize(n)
        # Go through each one and parse it out
        for c in jd[n]['colors']:
            sizeTemp = sizeC(c)
            numTemp = numC(c)
            # Check if it's a shirt or shoe size
            if sizeTemp or numTemp:
                # Mark it for removal
                removal.append(c)
        # Remove everything that's marked
        for r in removal:
            jd[n]['colors'].remove(r)
        # Once irrelevant elements are done, start entering data
        # Python used Rest!
        SyS.slp(1)
        
        ### I'm just going to trust my past self here for now and move past it, beginning comment ###
        # Before we get too far, we check to see if there are too many variants to fit into one product
        # See how many sizes we have
        numOfSizes = 0
        if len(shirt_sizes) != 0:
            numOfSizes = len(shirt_sizes)
        if len(shoe_sizes) != 0:
            numOfSizes = numOfSizes + len(shoe_sizes)
        # Figure out how many total variants we will have in the end
        variantsTotal = len(jd[n]['colors'] * numOfSizes)
        # If there are more than 100 variants, we need to do one of the below
        # While there's more than 100 variants total
        while variantsTotal > 100:
            # 1) Add an extra option that will allow for fewer variants
            if len(shirt_sizes) > 0:
                shirt_sizes[-2] = shirt_sizes[-2] + '/' + shirt_sizes[-1]
                shirt_sizes.remove(shirt_sizes[-1])
                form_needed = True
                numOfSizes = numOfSizes - 1
                variantsTotal = len(jd[n]['colors'] * numOfSizes)
                if variantsTotal <= 100:
                    # Python used Brick Break!
                    break
            # 2) Make two identical products with different colors and sizes
            if len(shoe_sizes) > 0:
                shoe_sizes[-2] = shoe_sizes[-2] + '/' + shoe_sizes[-1]
                shoe_sizes.remove(shoe_sizes[-1])
                form_needed = True
                numOfSizes = numOfSizes - 1
                variantsTotal = len(jd[n]['colors'] * numOfSizes)
                if variantsTotal <= 100:
                    # Python used Brick Break!
                    break
        # However, pants have to be handled differently
        if category == 'pants' and variantsTotal > 100:
            # Create an list for the formatted pants sizes (p_s)
            p_s = []
            # For every entry in the shirt sizes (also pantSizes)
            for s in shirt_sizes:
                # Append the size, but split into its two parts
                p_s.append(s.split(' x '))
            w_s, l_s = format_pants(p_s)
            if 'UNF' not in l_s:
                l_form_needed = True
            else:
                unf_form_needed = True
            widths = w_s
        ### End comment ###
        
        ############################################################
        # BEGINNING PROCESS OF ACTUALLY ADDING ITEMS TO THE DATABASE
        ############################################################
        # A. Base page, Add Product, Physical Product Buttons (Generic information, should not require much modification)
        # Add Button
        # Set up add button as a None value
        add = None
        # While it's a None value
        while add is None:
            # Try to find the button
            try:
                # Via the default browser method
                add = browser.find_by_xpath('//div[contains(@class, "label-add-product")]')[0]
            # If that doesn't work
            except:
                # Python used Rest!
                SyS.slp2()
        # Try to click the add button
        try:
            # Python used Pound!
            add.click()
        except exceptions.WebDriverException:
            # It wasn't very effective...
            addB = browser.driver.find_element_by_css_selector('.label-add-product')
            action = ActionChains(browser.driver)
            action.move_to_element_with_offset(addB, 5, 5)
            # Python used Pound!
            action.click()
            action.perform()
            # Python used Rest!
            SyS.slp2()
        # Physical Button
        # Python used Rest!
        SyS.slp3()
        # Try to find the physical button
        try:
            physical = WebDriverWait(browser.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-value="store-item-physical"]')))
        except exceptions.WebDriverException:
            # It wasn't very effective...
            addB = browser.driver.find_element_by_css_selector('.label-add-product')
            action = ActionChains(browser.driver)
            action.move_to_element_with_offset(addB, 5, 5)
            # Python used Pound!
            action.click()
            action.perform()
            # Python used Rest!
            SyS.slp2()
            # Click the add button again
            try:
                # Python used Pound!
                add.click()
                # Python used Rest!
                SyS.slp2()
            except:
                pass
                # Python used Rest!
                SyS.slp2()
            # Try to find the physical button in the normal way
            try:
                physical = WebDriverWait(browser.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-value="store-item-physical"]')))
            # If that doesn't work
            except:
                # Set up physical as a None value
                physical = None
                # And while it's None
                while physical is None:
                    # Try to find the physical button
                    try:
                        # Using the default way in the browser
                        physical = browser.find_by_xpath('//div[@data-value="store-item-physical"]')[0]
                    # Otherwise
                    except:
                        # Python used Rest!
                        SyS.slp2()
            # Python used Rest!
            SyS.slp2()
        # Python used Pound!
        try:
            physical.click()
        except:
            # It wasn't very effective...
            # Click outside of it once to get to the base window
            addB = browser.driver.find_element_by_css_selector('.label-add-product')
            action = ActionChains(browser.driver)
            action.move_to_element_with_offset(addB, 5, 5)
            # Python used Pound!
            action.click()
            action.perform()
            # Python used Rest!
            SyS.slp2()
            # Find this physical tag again and press it
            try:
                physical = WebDriverWait(browser.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "icon-store-item-physical")))
            except:
                physical = WebDriverWait(browser.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-value="store-item-physical"]')))
            # Python used Rest!
            SyS.slp2()
            # Python used Pound!
            physical.click()
        # Create an empty tab variable for the moment to ensure that it gets filled
        # Main tab
        itemTab = None
        # Until it does get filled
        while itemTab is None:
            # Try assigning it
            try:
                itemTab = SpS.xpath('//div[contains(text(), "Item")]')
            # If that doesn't work and it timed out due to lag
            except TimeoutException:
                # It wasn't very effective...
                # Python used Rest!
                SyS.slp2()
                # # Re-assign that button
                itemTab = SpS.xpath('//div[contains(text(), "Item")]')
            # If both fail, the while loops back to the top here
        # Variants/Options Tab
        variantsTab = SpS.xpath('//div[contains(text(), "Variants")]')
        # Additional Information Tab
        additionalTab = SpS.xpath('//div[contains(text(), "Additional")]')
        # Form tab
        formTab = SpS.xpath('//div[contains(text(), "Form")]')
        # Options Tab
        optionsTab = SpS.xpath('//div[contains(text(), "Options")]')
        # Social Tab
        socialTab = SpS.xpath('//div[contains(text(), "Social")]')
        # NOTE: The following will remain until all tabs have been clicked
        # logging.debug(additionalTab, formTab, optionsTab, socialTab)
        
        # B. Main Add Page, Images, Name, Desc. (Once again generic, little to no personal modification required)
        # Start Main Tab Work
        # Find the title entry
        title = SpS.name("title")
        # Python used Pound!
        # title.click()
        # Send the SpS.name of the item
        title.type(jd[n]['origin'] + ' ' + n)
        # Python used Rest!
        SyS.slp3()
        
        # Item Description
        # Send it over to the right method
        updateGivenDesc(jd[n]['description'], jd[n]['origin'])
        # Python used Rest!
        SyS.slp3()
        # Parse tags out of the description
        updateTags(jd[n]['origin'] + ' ' + n)
        # Python used Rest!
        SyS.slp3()
        
        # Store Visibility
        # Find the visibility thing
        vis_thing = SpS.css('div.clear.field-workflow-wrapper')
        visibility = vis_thing
        # Try to click the visibility normally
        try:
            # Python used Pound!
            visibility.click()
        except:
            # Move to the element
            SpS.move_to(visibility)
            # Create an Action Chain
            ac = ActionChains(browser.driver)
            # Python used Pound!
            ac.click()
            # Perform the action
            ac.perform()
        # Only loadable directly after above click call
        WebDriverWait(browser.driver, 3).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'workflow-flyout-options')))  # 0 is visible, 1 is scheduled, 2 is hidden
        options = SpS.csss('div.field-workflow-flyout-option-wrapper')
        try:
            # Python used Pound!
            options[2].click()
        except:
            # Try to click the visibility normally
            try:
                # Python used Pound!
                visibility.click()
            except:
                # Move to the element
                SpS.move_to(visibility)
                # Create an Action Chain
                ac = ActionChains(browser.driver)
                # Python used Pound!
                ac.click()
                # Perform the action
                ac.perform()
            # Only loadable directly after above click call
            WebDriverWait(browser.driver, 3).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'workflow-flyout-options')))  # 0 is visible, 1 is scheduled, 2 is hidden
            options = SpS.csss('div.field-workflow-flyout-option-wrapper')
            try:
                # Python used Pound!
                options[2].click()
            except:
                pass
        
        # Images
        addImagesGiven(jd[n]['image_paths'])
        # Save total button for every page
        saveTotal = SpS.css('input.saveAndClose')
        
        # C. Variants Tab
        # Variants/Options Tab
        variantsTab = SpS.xpath('//div[contains(text(), "&")]')
        # Find the link that sends the browser to the variants tab
        click_to_variants = SpS.xpath('//div[@class="pricing"]')
        try:
            # Python used Pound!
            variantsTab.click()
        except:
            # Move to the element
            SpS.move_to(click_to_variants)
            # Create an ActionChain
            ac = ActionChains(browser.driver)
            # Python used Pound!
            ac.click()
            # Perform the ActionChain
            ac.perform()
        # Python used Rest!
        SyS.slp(1)
        
        # Adaptation for other clothing or non-clothing items would need to start here... (see line 2928)
        # ****************************************************************************************
        
        # Clicks a given tab inside the item page, local variant that uses previously found button, backup for global
        # method in SplinterShortcuts
        def click_tab(tab_text='Pricing & Variants'):
            counter = 0
            c_text = SpS.xpath('//div[contains(@class, "tab")]//div[contains(@class, "active")]')[0].text
            while c_text != tab_text and counter < 100:
                # Variants/Options Tab
                variantsTab = SpS.xpath('//div[contains(text(), "&")]')
                print(c_text)
                try:
                    # Python used Pound!
                    variantsTab.click()
                except:
                    try:
                        # Python used Pound!
                        click_to_variants.click()
                    except:
                        # Move to mouse over the element
                        SpS.move_to(variantsTab)
                        # Create an ActionChain
                        ac = ActionChains(browser.driver)
                        # Python used Pound!
                        ac.click()
                        # Perform the ActionChain
                        ac.perform()
                c_text = SpS.xpath('//div[contains(@class, "tab")]//div[contains(@class, "active")]')[0].text
                counter += 1
                
        
        # Shortcut method to add an option to the variants page
        def add_opt(opt_name='Color'):
            # Find Add Variant Option Button
            addOpt = SpS.css('div.add-option.pulse-warnable')
            try:
                # Python used Pound!
                addOpt.click()
            except:
                try:
                    # Python used Pound!
                    click_to_variants.click()
                except:
                    # Move to mouse over the element
                    SpS.move_to(variantsTab)
                    # Create an ActionChain
                    ac = ActionChains(browser.driver)
                    # Python used Pound!
                    ac.click()
                    # Perform the ActionChain
                    ac.perform()
                # Python used Rest!
                SyS.slp(1)
                # Python used Pound!
                addOpt.click()
            # Find the option name field and put the name in it
            optionName = WebDriverWait(browser.driver, 3).until(EC.presence_of_element_located((By.NAME, 'optionName')))
            # Python used Pound!
            optionName.click()
            optionName.send_keys(opt_name)
            # Python used Rest!
            SyS.slp(1)
            # Save the new option
            saveOption = SpS.css('input.save')
            # Python used Pound!
            saveOption.click()
            
            
        # Begin necessary variant option initialization(s)
        if len(jd[n]['colors']) > 1:
            # Use the above method to click the tab
            SpS.select_tab('Pricing & Variants')
            # Python used Rest!
            SyS.slp(1)
            # Find Add Variant Option Button
            add_opt('Color')
            # Python used Rest!
            SyS.slp(1)
        # Now, create the Size option
        sizes = []
        # If we're dealing with a shirt, use the proper sizes
        if len(shirt_sizes) > 0:
            sizes = shirt_sizes
        # If we're dealing with shoes, use the proper sizes
        elif len(shoe_sizes) > 0:
            sizes = shoe_sizes
        # If widths have been determined due to size, set the sizes to the widths
        if len(widths) > 0:
            sizes = widths
        # If sizes are a thing, create the option
        # Details: Must be more than one size and must either A) not be a pants or shirts item or B) be a shorts or pants item with a form enabled
        if len(sizes) >= 1 and ((category != 'pants' and category != 'shorts') or len(
                pant_sizes) == 0 or l_form_needed or unf_form_needed):
            # Python used Pound!
            SpS.select_tab()
            # Python used Rest!
            SyS.slp(1)
            # Find and click the add option button
            add_opt('Size')
            SyS.slp(1)
        # Otherwise, if it is a pants or shorts item and it doesn't need a form, include all of the sizing options here
        elif len(sizes) >= 1 and (category == 'pants' or category == 'shorts') and \
                len(pant_sizes) != 0 and not l_form_needed and not unf_form_needed:
            # Python used Pound!
            SpS.select_tab()
            # Python used Rest!
            SyS.slp(1)
            add_opt('Size W')
            SyS.slp(1)
            add_opt('Size L')
            SyS.slp(1)
        
        # TODO: Continue from here last time, shortcut methods above semi-tested and proven successful thus far, more
        # TODO: tests and methods to come next time
        # Start by adding the first sku
        sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
        # Python used Rest!
        SyS.slp3()
        # Python used Pound!
        sku.click()
        # Python used Rest!
        SyS.slp2()
        # Create a variable to enter for the SKU
        skuString = ''
        # Check and see if there's an actual SKU variable in the data
        try:
            skuString = jd[n]['skus'][0]
        # If not, find it elsewhere
        except:
            skuString = jd[n]['basesku'][6:]
        # Add the size info if necessary
        if len(sizes) >= 1:
            skuString = skuString + str(sizes[0])
        # Send the SKU over
        sku.type(skuString)
        # Price addition
        varPrice = SpS.css('div.rows>div:last-of-type div.attribute-pricing')
        # Python used Pound!
        varPrice.click()
        # Find the input field and send the info there
        priceIn = SpS.css('input[name="price"]')
        try:
            priceIn.click()
        except:
            pass
        try:
            priceIn.type(jd[n]['price'] + Keys.ENTER)
        except:
            browser.type('price', jd[n]['price'] + Keys.ENTER)
        # Python used Rest!
        SyS.slp2()
        
        # INITIAL VARIANT ADDITION
        # ------------------------
        
        # Inventory
        marked = False
        
        # Method to mark infinite stock
        def mark_stock(val='inf'):
            global marked
            # Find the stock attribute
            stock = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-stock.attribute')
            # Python used Pound!
            stock.click()
            # Python used Rest!
            SyS.slp(1)
            if val == 'inf':
                if not marked:
                    # Check the box to mark unlimited stock
                    qty = WebDriverWait(browser.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
                    # Python used Pound!
                    qty.click()
                    marked = True
            else:
                if not marked:
                    browser.find_by_xpath('//input[@name="qtyInStock"]')[0].type(str(val))
                else:
                    # Check the box to mark unlimited stock
                    qty = WebDriverWait(browser.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sqs-basic-check')))
                    # Python used Rest
                    SyS.slp(1)
                    # Python used Pound!
                    qty.click()
                    # Python used Rest
                    SyS.slp(1)
                    # Type the now open quantity field in
                    browser.find_by_xpath('//input[@name="qtyInStock"]')[0].type(str(val))
                    marked = False
        # Find the stock attribute
        #stock = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-stock.attribute')
        # Python used Pound!
        #stock.click()
        # Python used Rest!
        SyS.slp2()
        if jd[n]['origin'] not in inventory_dependents:
           mark_stock()
        # TODO: Continue here, above statement needs to be removed/replaced with better parsing
        else:
            mark_stock('0')
        
        def type_color(col):
            # Find the input
            color = SpS.css('div.rows>div:last-of-type div.attribute[name="Color"] input')
            # Python used Pound!
            color.click()
            # Python used Rest!
            SyS.slp2()
            # Try sending it, if it doesn't go through (which it always should) don't worry about it
            try:
                color.type(col)
            except:
                pass
        
        # Color
        if len(jd[n]['colors']) > 1:
            # Color typing
            type_color(jd[n]['colors'][0])
        
        # Sizes
        if len(sizes) >= 1 and ((category != 'pants' and category != 'shorts') or len(
                pant_sizes) == 0 or l_form_needed or unf_form_needed):
            # TODO: Convert this to method
            # region ShouldBeMethod
            cc = jd[n]['colors'][0]
            # Find the size option and click it
            size = SpS.css('div.rows>div:last-of-type div.attribute:last-of-type input')
            # Python used Pound!
            size.click()
            # Send the first size over
            size.type(sizes[0])
            try:
                if sizes[0] not in jd[n]['color_data'][cc]:
                    mark_stock('0')
                else:
                    mark_stock()
            except:
                print('Something wrong')
            # Add another duplicate variant with a different size for each size available, if there are none this won't run
            for s in range(1, len(sizes)):
                # Find and click the add variant button
                addVariant = WebDriverWait(browser.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.add-variant')))
                # Python used Pound!
                addVariant.click()
                # SKU
                sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                # Python used Pound!
                sku.click()
                # Python used Rest!
                SyS.slp3()
                # Send the correct SKU to the SKU field
                # If it's a number, add the extra notation for clarification
                if isNumber(sizes[s]):
                    sku.type(jd[n]['skus'][0] + 'S' + sizes[s])
                # Otherwise, just add the size
                else:
                    sku.type(jd[n]['skus'][0] + sizes[s])
                # Find the size
                size = SpS.css('div.rows>div:last-of-type div.attribute:last-of-type input')
                # Python used Pound!
                size.click()
                # Send the right size
                size.type(sizes[s])
                try:
                    if sizes[s] not in jd[n]['color_data'][cc]:
                        mark_stock('0')
                    else:
                        mark_stock()
                except:
                    print('Something wrong')
            # endregion
        # Start pants size input
        elif len(sizes) >= 1 and (category == 'pants' or category == 'shorts') and len(
                pant_sizes) != 0 and not l_form_needed and not unf_form_needed:
            # region ShouldBeMethod
            sizew = SpS.xpaths('//div[@class="attribute"]//input')[-2]
            sizel = SpS.xpaths('//div[@class="attribute"]//input')[-1]
            # Python used Pound!
            sizew.click()
            pantsSizes = []
            for s in sizes:
                pantsSizes.append(s.split(' x '))
            # Send the first size over
            sizew.type(pantsSizes[0][0])
            # Then find the second input
            sizel.click()
            # And send that size over
            sizel.type(pantsSizes[0][1])
            # Add another duplicate variant with a different size for each size available, if there are none this won't run
            for s in range(1, len(pantsSizes)):
                # Find and click the add variant button
                addVariant = WebDriverWait(browser.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.add-variant')))
                # Python used Pound!
                addVariant.click()
                # SKU
                sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                # Python used Pound!
                sku.click()
                # Python used Rest!
                SyS.slp3()
                # Send the correct SKU to the SKU field
                sku.type(jd[n]['skus'][0] + pantsSizes[s][0] + pantsSizes[s][1])
                ## Note: Although less efficient, find all elements first guarantees that the right w & l sizes will be selected by simply selecting ##
                ## the last two possible attributes on the list, which are the current ones ##
                # Get all of the attribute elements
                attrs = SpS.xpaths('//div[@class="attribute"]//input')
                # Find the W size
                sizew = attrs[-2]
                # Python used Pound!
                sizew.click()
                # Send the w size
                sizew.type(pantsSizes[s][0])
                # Find the L size
                sizel = attrs[-1]
                # Python used Pound!
                sizel.click()
                # Send the L size
                sizel.type(pantsSizes[s][1])
            # endregion
        # START ADDING VARIANTS
        # ---------------------
        for j in range(1, len(jd[n]['colors'])):
            # Find and click the add variant button
            addVariant = WebDriverWait(browser.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.add-variant')))
            # Python used Pound!
            addVariant.click()
            # SKU
            sku = SpS.css('div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
            # Try to just hit the SKU field
            try:
                # Python used Pound!
                sku.click()
            # If it doesn't work, act accordingly
            except exceptions.WebDriverException:
                # Find and click the confirm button
                confirmButton = SpS.css('.confirmation-button.no-frame.confirm')
                # Python used Rest!
                SyS.slp3()
                # Python used Pound!
                confirmButton.click()
                # Python used Rest!
                SyS.slp3()
                # Python used Pound!
                sku.click()
            # Python used Rest!
            SyS.slp2()
            # Get the String for the SKU
            skuString = jd[n]['skus'][j]
            # Create an list for the pant sizes in case we need it
            pantsSizes = []
            # Add the Size notation to the SKU if there's more than one and it's not a pants type
            if len(sizes) >= 1 and ((category != 'pants' and category != 'shorts') or len(
                    pant_sizes) == 0 or l_form_needed or unf_form_needed):
                skuString = skuString + str(sizes[0])
            # If there's more than one and it's a pants type, handle that as well
            elif len(sizes) >= 1 and (category == 'pants' or category == 'shorts') and len(
                    pant_sizes) != 0 and not l_form_needed and not unf_form_needed:
                for s in sizes:
                    # First split the size by an x in between the sizes
                    split_size = s.split(' x ')
                    # If that split didn't work, try the two numbers separated by a slash
                    if len(split_size) == 1 and '/' in s:
                        # Split the string
                        test = split_size.split('/')
                        # Set up a truth table
                        tests = [False, False]
                        # If the split was successful
                        if len(test) == 2:
                            # Make sure that at least one number is one each side of the slash
                            for z in zip('0123456789'):
                                if z[0] in test[0]:
                                    tests[0] = True
                                if z[0] in test[1]:
                                    tests[1] = True
                                # If this has been completed, break the loop
                                if tests[0] and tests[1]:
                                    break
                            # If this has proven successful, set this new split to the actual size values
                            if tests[0] and tests[1]:
                                split_size = test
                    pantsSizes.append(split_size)
                skuString = skuString + str(pantsSizes[0][0]) + str(pantsSizes[0][1])
            # Send the SKUs over
            sku.type(skuString)
            # Enter the color
            type_color(jd[n]['colors'][j])
            cc = jd[n]['colors'][j]
            # Normal Sizes
            if len(sizes) >= 1 and ((category != 'pants' and category != 'shorts') or len(
                    pant_sizes) == 0 or l_form_needed or unf_form_needed):
                size = SpS.css('div.rows>div:last-of-type div.attribute:last-of-type input')
                # Python used Pound!
                size.click()
                size.type(sizes[0])
                try:
                    if sizes[0] not in jd[n]['color_data'][cc]:
                        mark_stock('0')
                    else:
                        mark_stock()
                except:
                    pass
                for s in range(1, len(sizes)):
                    addVariant = WebDriverWait(browser.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.add-variant')))
                    # Python used Pound!
                    addVariant.click()
                    # checkForDialogVariants()
                    # SKU
                    sku = SpS.css(
                        'div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                    # checkForDialogVariants()
                    try:
                        # Python used Pound!
                        sku.click()
                    except exceptions.WebDriverException:
                        confirmButton = SpS.css('.confirmation-button.no-frame.confirm')
                        # Python used Pound!
                        confirmButton.click()
                        # Python used Rest!
                        SyS.slp3()
                        # Python used Pound!
                        sku.click()
                    # Python used Rest!
                    SyS.slp3()
                    sku.type(jd[n]['skus'][j] + sizes[s])
                    # Size
                    size = SpS.css('div.rows>div:last-of-type div.attribute:last-of-type input')
                    # Python used Pound!
                    size.click()
                    size.type(sizes[s])
                    try:
                        if sizes[s] not in jd[n]['color_data'][cc]:
                            mark_stock('0')
                        else:
                            mark_stock()
                    except:
                        print('Something else wrong')
            # Pants Sizes
            elif len(sizes) >= 1 and (category == 'pants' or category == 'shorts') and len(
                    pant_sizes) != 0 and not l_form_needed and not unf_form_needed:
                # Find the attribute objects
                attrs = SpS.xpaths('//div[@class="attribute"]//input')
                # Find the w size
                sizew = attrs[-2]
                # Python used Pound!
                sizew.click()
                # Send the w size over
                sizew.type(pantsSizes[0][0])
                # Find the l size
                sizel = attrs[-1]
                # Python used Pound!
                sizel.click()
                # Send the l size
                sizel.type(pantsSizes[0][1])
                # Python used Rest!
                SyS.slp2()
                # For the remaining sizes
                for s in range(1, len(pantsSizes)):
                    addVariant = WebDriverWait(browser.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.add-variant')))
                    # Python used Pound!
                    addVariant.click()
                    # checkForDialogVariants()
                    # SKU
                    sku = SpS.css(
                        'div.rows>div:last-of-type div.attributes div.attribute-sku.attribute input[name="sku"]')
                    # checkForDialogVariants()
                    try:
                        # Python used Pound!
                        sku.click()
                    except exceptions.WebDriverException:
                        confirmButton = SpS.css('.confirmation-button.no-frame.confirm')
                        # Python used Pound!
                        confirmButton.click()
                        # Python used Rest!
                        SyS.slp3()
                        # Python used Pound!
                        sku.click()
                    # Python used Rest!
                    SyS.slp3()
                    # Send the sku to the sku entry
                    sku.type(jd[n]['skus'][j] + pantsSizes[s][0] + pantsSizes[s][1])
                    # Update the attributes
                    attrs = SpS.xpaths('//div[@class="attribute"]//input')
                    # Find the w size
                    sizew = attrs[-2]
                    # Python used Pound!
                    sizew.click()
                    # Send the w size
                    sizew.type(pantsSizes[s][0])
                    # Find the l size
                    sizel = attrs[-1]
                    # Python used Pound!
                    sizel.click()
                    # Send the l size
                    sizel.type(pantsSizes[s][1])
        
        # End Variants Tab Work
        # ****************************************************************************************
        # ... and adaption work would end about here (see line 2523)
        
        # D. Details Page (More generic information, little to no work needed here)
        # Start Details Tab Work
        # Python used Rest!
        SyS.slp3()
        # Use previously created method to achieve this end
        updateDetailsWithData(n, jd)
        # End Details Page Work
        
        # If a form was required earlier, we now handle that form
        if form_needed:
            # Python used Pound!
            formTab.click()
            # Python used Rest!
            SyS.slp(1)
            formUsed = SpS.xpath('//div[@class="name" and contains(text(), "XXL")]')
            # Python used Pound!
            formUsed.click()
            # Python used Rest!
            SyS.slp3()
        # If a form for size is not required, but one for fit is, include it here
        elif fit_form_needed:
            # Python used Pound!
            formTab.click()
            # Python used Rest!
            SyS.slp(1)
            formUsed = SpS.xpath('//div[@class="name" and contains(text(), "Fit")]')
            # Python used Pound!
            formUsed.click()
            # Python used Rest!
            SyS.slp3()
        elif l_form_needed:
            # Python used Pound!
            formTab.click()
            # Python used Rest!
            SyS.slp(1)
            formUsed = SpS.xpath('//div[@class="name" and contains(text(), "Default")]')
            # Python used Pound!
            formUsed.click()
            # Python used Rest!
            SyS.slp3()
        elif unf_form_needed:
            # Python used Pound!
            formTab.click()
            # Python used Rest!
            SyS.slp(1)
            formUsed = SpS.xpath('//div[@class="name" and contains(text(), "UNF")]')
            # Python used Pound!
            formUsed.click()
            # Python used Rest!
            SyS.slp3()
        # Reset all of the variables used
        shirt_sizes = []
        shoe_sizes = []
        pant_sizes = []
        widths = []
        form_needed = False
        fit_form_needed = False
        l_form_needed = False
        unf_form_needed = False
        
        # Finally, Save and Close the item
        # Save total button for every page
        saveTotal = SpS.css('input.saveAndClose')
        # Python used Pound!
        saveTotal.click()
        # Python used Rest!
        SyS.slp(1)
        # Finally, increment the counter and check to see if it's time to update
        counter += 1
        current_length += 1
        if counter % 15 == 1 and counter != 1:
            try:
                browser.refresh()
            except:
                browser.reload()
            SyS.slp(3)
    # ========= End For ===========
    #########################################################
    # ENDING PROCESS OF ACTUALLY ADDING ITEMS TO THE DATABASE
    #########################################################
    # If items have been added, create a prompt that will notify the user of those items
    if counter > 0:
        # Print the total number of items to the console
        logging.debug('Completed ' + str(counter) + ' items.')
        # Create a new window
        '''root = Tk()
        # Create the label necessary and pack it
        note = Label(root, text = counter + " new items have been added to the store! Please review them before making them visible.")
        note.pack()
        # Start the prompt window, the program will continue after the user closes the window
        root.mainloop()'''


# endregion

# region New Pages

# Runs upon discovering that the catalog has updated again
# Creates a page for the new season, and then adds it to the information file
def new_season_page():
    # Get the current season
    currentSeason = get_season(date.today())
    # Get the year
    currentYear = datetime.now().year
    # Try to hit the back button
    try:
        # Get the back button
        backToMenuButton = WebDriverWait(browser.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@data-label="menuHeader-back"]')))
        # Python used Pound!
        backToMenuButton.click()
        # Python used Rest!
        SyS.slp(1)
    # It's super effective!
    # It's not very effective...
    except:
        # If there's still an interface up, click somewhere to stop the interface
        # Find the Add Product Button
        '''addB = css('.label-add-product')
        # Start a new action chain
        action = ActionChains(browser.driver)
        # Move the cursor near the button
        action.move_to_element_with_offset(addB, 5, 5)
        # Python used Pound!
        action.click()
        action.perform()
        # Python used Rest!
        slp2()'''
        backToMenuButton = WebDriverWait(browser.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@data-label="menuHeader-back"]')))
        # Python used Pound!
        backToMenuButton.click()
        # Python used Rest!
        SyS.slp(1)
    # Begin adding the new page
    addPage = WebDriverWait(browser.driver, 3).until(EC.visibility_of_element_located(
        (By.XPATH, '(//footer/div[@class="add-page"]/span[@class="icon icon-add"])[last()]')))
    # Python used Pound!
    addPage.click()
    # Python used Rest!
    SyS.slp3()
    # Select the products page option
    productsAdd = WebDriverWait(browser.driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, '//div[@class="option icon-products"][last()]')))
    # Python used Pound!
    productsAdd.click()
    # Python used Rest!
    SyS.slp3()
    # Go to the newly created page
    newPage = SpS.css('div.sqs-navigation-bar-content>div:last-of-type div.sqs-navigation-item-content:first-of-type')
    # Attempt to send the name through
    try:
        # Python used Pound!
        newPage.type(currentSeason + ' ' + str(currentYear) + ' ' + 'Store')
    except:
        # If it doesn't work it doesn't matter because now we've moved on
        pass
    # Python used Rest!
    SyS.slp(3)
    # Click on the settings for this page
    settings = SpS.xpath('//div[@title="Products Settings"]')
    # Python used Pound!
    settings.click()
    # Change the name for the page
    pageName = WebDriverWait(browser.driver, 3).until(EC.visibility_of_element_located((By.NAME, 'navigationTitle')))
    # Python used Rest!
    SyS.slp2()
    # Python used Pound!
    pageName.click()
    # Erase the current name
    SpS.select_all_and_erase(pageName)
    # Send the name from the current season and year
    pageName.send_keys(currentSeason, currentYear, 'Store')
    # Python used Rest!
    SyS.slp2()
    # Change the page url
    pageURL = SpS.xpath('//input[@name="urlId"]')
    # Python used Pound!
    pageURL.click()
    # Erase the current url
    SpS.select_all_and_erase(pageURL)
    # Send the url from the current season and year
    pageURL.type('shop-' + currentSeason.lower + '-' + currentYear)
    # Find the save page button
    saveNewPage = SpS.css('div.button-holder div.button-block input.saveAndClose')
    # Python used Pound!
    saveNewPage.click()
    # Python used Rest!
    SyS.slp2()
    # Write the new entry to information.py
    f = open("information.py", "a+")
    currentUrl = unicodedata.normalize('NFKD', browser.url).encode('ascii', 'ignore')
    f.write("\n  INVENTORY_PAGE_" + currentSeason + "_" + str(currentYear) + " = \'" + currentUrl + "\'")
    f.close()
    Info = importlib.reload(information)


# End new_season_page

# Creates a new page for the shop to use once the exceeded amount of 200 items has been met
def new_shop_page(page_number):
    # Try to hit the back button
    try:
        # Get the back button
        backToMenuButton = WebDriverWait(browser.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@data-label="menuHeader-back"]')))
        # Python used Pound!
        backToMenuButton.click()
        # Python used Rest!
        SyS.slp(1)
    # It's not very effective...
    except:
        # Just try it again
        backToMenuButton = WebDriverWait(browser.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@data-label="menuHeader-back"]')))
        # Python used Pound!
        backToMenuButton.click()
        # Python used Rest!
        SyS.slp(1)
    # Begin adding the new page
    addPage = WebDriverWait(browser.driver, 3).until(EC.visibility_of_element_located(
        (By.XPATH, '(//footer/div[@class="add-page"]/span[@class="icon icon-add"])[last()]')))
    # Python used Pound!
    addPage.click()
    # Python used Rest!
    SyS.slp3()
    # Select the products page option
    productsAdd = WebDriverWait(browser.driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, '//div[@class="option icon-products"][last()]')))
    # Python used Pound!
    productsAdd.click()
    # Python used Rest!
    SyS.slp3()
    # Go to the newly created page
    newPage = SpS.css('div.sqs-navigation-bar-content>div:last-of-type div.sqs-navigation-item-content:first-of-type')
    # Attempt to send the name through
    try:
        # Python used Pound!
        newPage.type('Store' + str(page_number))
    except:
        # If it doesn't work it doesn't matter because now we've moved on
        pass
    # Python used Rest!
    SyS.slp(3)
    # Click on the settings for this page
    settings = SpS.xpath('//div[@title="Products Settings"]')
    # Python used Pound!
    settings.click()
    # Change the name for the page
    pageName = WebDriverWait(browser.driver, 3).until(EC.visibility_of_element_located((By.NAME, 'navigationTitle')))
    # Python used Rest!
    SyS.slp2()
    # Python used Pound!
    pageName.click()
    # Erase the current name
    SpS.select_all_and_erase(pageName)
    # Send the name from the current season and year
    pageName.send_keys('Shop ' + str(page_number))
    # Python used Rest!
    SyS.slp2()
    # Change the page url
    pageURL = SpS.xpath('//input[@name="urlId"]')
    # Python used Pound!
    pageURL.click()
    # Erase the current url
    SpS.select_all_and_erase(pageURL)
    # Send the url from the current season and year
    pageURL.type('shop-' + str(page_number))
    # Find the save page button
    saveNewPage = SpS.css('div.button-holder div.button-block input.saveAndClose')
    # Python used Pound!
    saveNewPage.click()
    # Python used Rest!
    SyS.slp2()
    # Write the new entry to information.py
    f = open("information.py", "a+")
    currentUrl = unicodedata.normalize('NFKD', browser.url).encode('ascii', 'ignore')
    f.write("\n  STORE_PAGE_" + str(page_number) + " = \'" + currentUrl + "\'")
    f.close()
    # Python used Rest!
    SyS.slp(2)
    # Delete the existing instance of the information module
    del sys.modules['information']
    # Re-import the module
    import information
    # Grab the global instantation of the class within the module
    global Info
    # Set the original instance of the class to an instance of the new class
    Info = information.Info
    # Reload the urls
    get_current_urls()


# Exits the browser and effectively quits the program
def finalize():
    global browser
    browser.quit()


# endregion

# ----------------- END PROGRAM METHODS ---------------------

# ----------------- SETUP EXIT FUNCTION ---------------------

atexit.register(finalize)

# ------------------ END EXIT FUNCTION ----------------------


# Class to help find out what color an image is, and thus what variant is belongs to

# region Color Class

"""
Original Author  Ernesto P. Adorio, Ph.D
Original Source: http://my-other-life-as-programmer.blogspot.com/2012/02/python-finding-nearest-matching-color.html
Modifed By: JDiscar
This class maps an RGB value to the nearest color name it can find. Code is modified to include
ImageMagick names and WebColor names.
1. Modify the minimization criterion to use least sum of squares of the differences.
2. Provide error checking for input R, G, B values to be within the interval [0, 255].
3. Provide different ways to specify the input RGB values, aside from the (R, G, B) values as done in the program above.
"""


class ColorNames:
    # Src: http://www.w3schools.com/html/html_colornames.asp
    WebColorMap = {}
    WebColorMap["AliceBlue"] = "#F0F8FF"
    WebColorMap["AntiqueWhite"] = "#FAEBD7"
    WebColorMap["Aqua"] = "#00FFFF"
    WebColorMap["Aquamarine"] = "#7FFFD4"
    WebColorMap["Azure"] = "#F0FFFF"
    WebColorMap["Beige"] = "#F5F5DC"
    WebColorMap["Bisque"] = "#FFE4C4"
    WebColorMap["Black"] = "#000000"
    WebColorMap["BlanchedAlmond"] = "#FFEBCD"
    WebColorMap["Blue"] = "#0000FF"
    WebColorMap["BlueViolet"] = "#8A2BE2"
    WebColorMap["Brown"] = "#A52A2A"
    WebColorMap["BurlyWood"] = "#DEB887"
    WebColorMap["CadetBlue"] = "#5F9EA0"
    WebColorMap["Chartreuse"] = "#7FFF00"
    WebColorMap["Chocolate"] = "#D2691E"
    WebColorMap["Coral"] = "#FF7F50"
    WebColorMap["CornflowerBlue"] = "#6495ED"
    WebColorMap["Cornsilk"] = "#FFF8DC"
    WebColorMap["Crimson"] = "#DC143C"
    WebColorMap["Cyan"] = "#00FFFF"
    WebColorMap["DarkBlue"] = "#00008B"
    WebColorMap["DarkCyan"] = "#008B8B"
    WebColorMap["DarkGoldenRod"] = "#B8860B"
    WebColorMap["DarkGray"] = "#A9A9A9"
    WebColorMap["DarkGrey"] = "#A9A9A9"
    WebColorMap["DarkGreen"] = "#006400"
    WebColorMap["DarkKhaki"] = "#BDB76B"
    WebColorMap["DarkMagenta"] = "#8B008B"
    WebColorMap["DarkOliveGreen"] = "#556B2F"
    WebColorMap["Darkorange"] = "#FF8C00"
    WebColorMap["DarkOrchid"] = "#9932CC"
    WebColorMap["DarkRed"] = "#8B0000"
    WebColorMap["DarkSalmon"] = "#E9967A"
    WebColorMap["DarkSeaGreen"] = "#8FBC8F"
    WebColorMap["DarkSlateBlue"] = "#483D8B"
    WebColorMap["DarkSlateGray"] = "#2F4F4F"
    WebColorMap["DarkSlateGrey"] = "#2F4F4F"
    WebColorMap["DarkTurquoise"] = "#00CED1"
    WebColorMap["DarkViolet"] = "#9400D3"
    WebColorMap["DeepPink"] = "#FF1493"
    WebColorMap["DeepSkyBlue"] = "#00BFFF"
    WebColorMap["DimGray"] = "#696969"
    WebColorMap["DimGrey"] = "#696969"
    WebColorMap["DodgerBlue"] = "#1E90FF"
    WebColorMap["FireBrick"] = "#B22222"
    WebColorMap["FloralWhite"] = "#FFFAF0"
    WebColorMap["ForestGreen"] = "#228B22"
    WebColorMap["Fuchsia"] = "#FF00FF"
    WebColorMap["Gainsboro"] = "#DCDCDC"
    WebColorMap["GhostWhite"] = "#F8F8FF"
    WebColorMap["Gold"] = "#FFD700"
    WebColorMap["GoldenRod"] = "#DAA520"
    WebColorMap["Gray"] = "#808080"
    WebColorMap["Grey"] = "#808080"
    WebColorMap["Green"] = "#008000"
    WebColorMap["GreenYellow"] = "#ADFF2F"
    WebColorMap["HoneyDew"] = "#F0FFF0"
    WebColorMap["HotPink"] = "#FF69B4"
    WebColorMap["IndianRed"] = "#CD5C5C"
    WebColorMap["Indigo"] = "#4B0082"
    WebColorMap["Ivory"] = "#FFFFF0"
    WebColorMap["Khaki"] = "#F0E68C"
    WebColorMap["Lavender"] = "#E6E6FA"
    WebColorMap["LavenderBlush"] = "#FFF0F5"
    WebColorMap["LawnGreen"] = "#7CFC00"
    WebColorMap["LemonChiffon"] = "#FFFACD"
    WebColorMap["LightBlue"] = "#ADD8E6"
    WebColorMap["LightCoral"] = "#F08080"
    WebColorMap["LightCyan"] = "#E0FFFF"
    WebColorMap["LightGoldenRodYellow"] = "#FAFAD2"
    WebColorMap["LightGray"] = "#D3D3D3"
    WebColorMap["LightGrey"] = "#D3D3D3"
    WebColorMap["LightGreen"] = "#90EE90"
    WebColorMap["LightPink"] = "#FFB6C1"
    WebColorMap["LightSalmon"] = "#FFA07A"
    WebColorMap["LightSeaGreen"] = "#20B2AA"
    WebColorMap["LightSkyBlue"] = "#87CEFA"
    WebColorMap["LightSlateGray"] = "#778899"
    WebColorMap["LightSlateGrey"] = "#778899"
    WebColorMap["LightSteelBlue"] = "#B0C4DE"
    WebColorMap["LightYellow"] = "#FFFFE0"
    WebColorMap["Lime"] = "#00FF00"
    WebColorMap["LimeGreen"] = "#32CD32"
    WebColorMap["Linen"] = "#FAF0E6"
    WebColorMap["Magenta"] = "#FF00FF"
    WebColorMap["Maroon"] = "#800000"
    WebColorMap["MediumAquaMarine"] = "#66CDAA"
    WebColorMap["MediumBlue"] = "#0000CD"
    WebColorMap["MediumOrchid"] = "#BA55D3"
    WebColorMap["MediumPurple"] = "#9370D8"
    WebColorMap["MediumSeaGreen"] = "#3CB371"
    WebColorMap["MediumSlateBlue"] = "#7B68EE"
    WebColorMap["MediumSpringGreen"] = "#00FA9A"
    WebColorMap["MediumTurquoise"] = "#48D1CC"
    WebColorMap["MediumVioletRed"] = "#C71585"
    WebColorMap["MidnightBlue"] = "#191970"
    WebColorMap["MintCream"] = "#F5FFFA"
    WebColorMap["MistyRose"] = "#FFE4E1"
    WebColorMap["Moccasin"] = "#FFE4B5"
    WebColorMap["NavajoWhite"] = "#FFDEAD"
    WebColorMap["Navy"] = "#000080"
    WebColorMap["OldLace"] = "#FDF5E6"
    WebColorMap["Olive"] = "#808000"
    WebColorMap["OliveDrab"] = "#6B8E23"
    WebColorMap["Orange"] = "#FFA500"
    WebColorMap["OrangeRed"] = "#FF4500"
    WebColorMap["Orchid"] = "#DA70D6"
    WebColorMap["PaleGoldenRod"] = "#EEE8AA"
    WebColorMap["PaleGreen"] = "#98FB98"
    WebColorMap["PaleTurquoise"] = "#AFEEEE"
    WebColorMap["PaleVioletRed"] = "#D87093"
    WebColorMap["PapayaWhip"] = "#FFEFD5"
    WebColorMap["PeachPuff"] = "#FFDAB9"
    WebColorMap["Peru"] = "#CD853F"
    WebColorMap["Pink"] = "#FFC0CB"
    WebColorMap["Plum"] = "#DDA0DD"
    WebColorMap["PowderBlue"] = "#B0E0E6"
    WebColorMap["Purple"] = "#800080"
    WebColorMap["Red"] = "#FF0000"
    WebColorMap["RosyBrown"] = "#BC8F8F"
    WebColorMap["RoyalBlue"] = "#4169E1"
    WebColorMap["SaddleBrown"] = "#8B4513"
    WebColorMap["Salmon"] = "#FA8072"
    WebColorMap["SandyBrown"] = "#F4A460"
    WebColorMap["SeaGreen"] = "#2E8B57"
    WebColorMap["SeaShell"] = "#FFF5EE"
    WebColorMap["Sienna"] = "#A0522D"
    WebColorMap["Silver"] = "#C0C0C0"
    WebColorMap["SkyBlue"] = "#87CEEB"
    WebColorMap["SlateBlue"] = "#6A5ACD"
    WebColorMap["SlateGray"] = "#708090"
    WebColorMap["SlateGrey"] = "#708090"
    WebColorMap["Snow"] = "#FFFAFA"
    WebColorMap["SpringGreen"] = "#00FF7F"
    WebColorMap["SteelBlue"] = "#4682B4"
    WebColorMap["Tan"] = "#D2B48C"
    WebColorMap["Teal"] = "#008080"
    WebColorMap["Thistle"] = "#D8BFD8"
    WebColorMap["Tomato"] = "#FF6347"
    WebColorMap["Turquoise"] = "#40E0D0"
    WebColorMap["Violet"] = "#EE82EE"
    WebColorMap["Wheat"] = "#F5DEB3"
    WebColorMap["White"] = "#FFFFFF"
    WebColorMap["WhiteSmoke"] = "#F5F5F5"
    WebColorMap["Yellow"] = "#FFFF00"
    WebColorMap["YellowGreen"] = "#9ACD32"
    
    # src: http://www.imagemagick.org/script/color.php
    ImageMagickColorMap = {}
    ImageMagickColorMap["snow"] = "#FFFAFA"
    ImageMagickColorMap["snow1"] = "#FFFAFA"
    ImageMagickColorMap["snow2"] = "#EEE9E9"
    ImageMagickColorMap["RosyBrown1"] = "#FFC1C1"
    ImageMagickColorMap["RosyBrown2"] = "#EEB4B4"
    ImageMagickColorMap["snow3"] = "#CDC9C9"
    ImageMagickColorMap["LightCoral"] = "#F08080"
    ImageMagickColorMap["IndianRed1"] = "#FF6A6A"
    ImageMagickColorMap["RosyBrown3"] = "#CD9B9B"
    ImageMagickColorMap["IndianRed2"] = "#EE6363"
    ImageMagickColorMap["RosyBrown"] = "#BC8F8F"
    ImageMagickColorMap["brown1"] = "#FF4040"
    ImageMagickColorMap["firebrick1"] = "#FF3030"
    ImageMagickColorMap["brown2"] = "#EE3B3B"
    ImageMagickColorMap["IndianRed"] = "#CD5C5C"
    ImageMagickColorMap["IndianRed3"] = "#CD5555"
    ImageMagickColorMap["firebrick2"] = "#EE2C2C"
    ImageMagickColorMap["snow4"] = "#8B8989"
    ImageMagickColorMap["brown3"] = "#CD3333"
    ImageMagickColorMap["red"] = "#FF0000"
    ImageMagickColorMap["red1"] = "#FF0000"
    ImageMagickColorMap["RosyBrown4"] = "#8B6969"
    ImageMagickColorMap["firebrick3"] = "#CD2626"
    ImageMagickColorMap["red2"] = "#EE0000"
    ImageMagickColorMap["firebrick"] = "#B22222"
    ImageMagickColorMap["brown"] = "#A52A2A"
    ImageMagickColorMap["red3"] = "#CD0000"
    ImageMagickColorMap["IndianRed4"] = "#8B3A3A"
    ImageMagickColorMap["brown4"] = "#8B2323"
    ImageMagickColorMap["firebrick4"] = "#8B1A1A"
    ImageMagickColorMap["DarkRed"] = "#8B0000"
    ImageMagickColorMap["red4"] = "#8B0000"
    ImageMagickColorMap["maroon"] = "#800000"
    ImageMagickColorMap["LightPink1"] = "#FFAEB9"
    ImageMagickColorMap["LightPink3"] = "#CD8C95"
    ImageMagickColorMap["LightPink4"] = "#8B5F65"
    ImageMagickColorMap["LightPink2"] = "#EEA2AD"
    ImageMagickColorMap["LightPink"] = "#FFB6C1"
    ImageMagickColorMap["pink"] = "#FFC0CB"
    ImageMagickColorMap["crimson"] = "#DC143C"
    ImageMagickColorMap["pink1"] = "#FFB5C5"
    ImageMagickColorMap["pink2"] = "#EEA9B8"
    ImageMagickColorMap["pink3"] = "#CD919E"
    ImageMagickColorMap["pink4"] = "#8B636C"
    ImageMagickColorMap["PaleVioletRed4"] = "#8B475D"
    ImageMagickColorMap["PaleVioletRed"] = "#DB7093"
    ImageMagickColorMap["PaleVioletRed2"] = "#EE799F"
    ImageMagickColorMap["PaleVioletRed1"] = "#FF82AB"
    ImageMagickColorMap["PaleVioletRed3"] = "#CD6889"
    ImageMagickColorMap["LavenderBlush"] = "#FFF0F5"
    ImageMagickColorMap["LavenderBlush1"] = "#FFF0F5"
    ImageMagickColorMap["LavenderBlush3"] = "#CDC1C5"
    ImageMagickColorMap["LavenderBlush2"] = "#EEE0E5"
    ImageMagickColorMap["LavenderBlush4"] = "#8B8386"
    ImageMagickColorMap["maroon"] = "#B03060"
    ImageMagickColorMap["HotPink3"] = "#CD6090"
    ImageMagickColorMap["VioletRed3"] = "#CD3278"
    ImageMagickColorMap["VioletRed1"] = "#FF3E96"
    ImageMagickColorMap["VioletRed2"] = "#EE3A8C"
    ImageMagickColorMap["VioletRed4"] = "#8B2252"
    ImageMagickColorMap["HotPink2"] = "#EE6AA7"
    ImageMagickColorMap["HotPink1"] = "#FF6EB4"
    ImageMagickColorMap["HotPink4"] = "#8B3A62"
    ImageMagickColorMap["HotPink"] = "#FF69B4"
    ImageMagickColorMap["DeepPink"] = "#FF1493"
    ImageMagickColorMap["DeepPink1"] = "#FF1493"
    ImageMagickColorMap["DeepPink2"] = "#EE1289"
    ImageMagickColorMap["DeepPink3"] = "#CD1076"
    ImageMagickColorMap["DeepPink4"] = "#8B0A50"
    ImageMagickColorMap["maroon1"] = "#FF34B3"
    ImageMagickColorMap["maroon2"] = "#EE30A7"
    ImageMagickColorMap["maroon3"] = "#CD2990"
    ImageMagickColorMap["maroon4"] = "#8B1C62"
    ImageMagickColorMap["MediumVioletRed"] = "#C71585"
    ImageMagickColorMap["VioletRed"] = "#D02090"
    ImageMagickColorMap["orchid2"] = "#EE7AE9"
    ImageMagickColorMap["orchid"] = "#DA70D6"
    ImageMagickColorMap["orchid1"] = "#FF83FA"
    ImageMagickColorMap["orchid3"] = "#CD69C9"
    ImageMagickColorMap["orchid4"] = "#8B4789"
    ImageMagickColorMap["thistle1"] = "#FFE1FF"
    ImageMagickColorMap["thistle2"] = "#EED2EE"
    ImageMagickColorMap["plum1"] = "#FFBBFF"
    ImageMagickColorMap["plum2"] = "#EEAEEE"
    ImageMagickColorMap["thistle"] = "#D8BFD8"
    ImageMagickColorMap["thistle3"] = "#CDB5CD"
    ImageMagickColorMap["plum"] = "#DDA0DD"
    ImageMagickColorMap["violet"] = "#EE82EE"
    ImageMagickColorMap["plum3"] = "#CD96CD"
    ImageMagickColorMap["thistle4"] = "#8B7B8B"
    ImageMagickColorMap["fuchsia"] = "#FF00FF"
    ImageMagickColorMap["magenta"] = "#FF00FF"
    ImageMagickColorMap["magenta1"] = "#FF00FF"
    ImageMagickColorMap["plum4"] = "#8B668B"
    ImageMagickColorMap["magenta2"] = "#EE00EE"
    ImageMagickColorMap["magenta3"] = "#CD00CD"
    ImageMagickColorMap["DarkMagenta"] = "#8B008B"
    ImageMagickColorMap["magenta4"] = "#8B008B"
    ImageMagickColorMap["purple"] = "#800080"
    ImageMagickColorMap["MediumOrchid"] = "#BA55D3"
    ImageMagickColorMap["MediumOrchid1"] = "#E066FF"
    ImageMagickColorMap["MediumOrchid2"] = "#D15FEE"
    ImageMagickColorMap["MediumOrchid3"] = "#B452CD"
    ImageMagickColorMap["MediumOrchid4"] = "#7A378B"
    ImageMagickColorMap["DarkViolet"] = "#9400D3"
    ImageMagickColorMap["DarkOrchid"] = "#9932CC"
    ImageMagickColorMap["DarkOrchid1"] = "#BF3EFF"
    ImageMagickColorMap["DarkOrchid3"] = "#9A32CD"
    ImageMagickColorMap["DarkOrchid2"] = "#B23AEE"
    ImageMagickColorMap["DarkOrchid4"] = "#68228B"
    ImageMagickColorMap["purple"] = "#A020F0"
    ImageMagickColorMap["indigo"] = "#4B0082"
    ImageMagickColorMap["BlueViolet"] = "#8A2BE2"
    ImageMagickColorMap["purple2"] = "#912CEE"
    ImageMagickColorMap["purple3"] = "#7D26CD"
    ImageMagickColorMap["purple4"] = "#551A8B"
    ImageMagickColorMap["purple1"] = "#9B30FF"
    ImageMagickColorMap["MediumPurple"] = "#9370DB"
    ImageMagickColorMap["MediumPurple1"] = "#AB82FF"
    ImageMagickColorMap["MediumPurple2"] = "#9F79EE"
    ImageMagickColorMap["MediumPurple3"] = "#8968CD"
    ImageMagickColorMap["MediumPurple4"] = "#5D478B"
    ImageMagickColorMap["DarkSlateBlue"] = "#483D8B"
    ImageMagickColorMap["LightSlateBlue"] = "#8470FF"
    ImageMagickColorMap["MediumSlateBlue"] = "#7B68EE"
    ImageMagickColorMap["SlateBlue"] = "#6A5ACD"
    ImageMagickColorMap["SlateBlue1"] = "#836FFF"
    ImageMagickColorMap["SlateBlue2"] = "#7A67EE"
    ImageMagickColorMap["SlateBlue3"] = "#6959CD"
    ImageMagickColorMap["SlateBlue4"] = "#473C8B"
    ImageMagickColorMap["GhostWhite"] = "#F8F8FF"
    ImageMagickColorMap["lavender"] = "#E6E6FA"
    ImageMagickColorMap["blue"] = "#0000FF"
    ImageMagickColorMap["blue1"] = "#0000FF"
    ImageMagickColorMap["blue2"] = "#0000EE"
    ImageMagickColorMap["blue3"] = "#0000CD"
    ImageMagickColorMap["MediumBlue"] = "#0000CD"
    ImageMagickColorMap["blue4"] = "#00008B"
    ImageMagickColorMap["DarkBlue"] = "#00008B"
    ImageMagickColorMap["MidnightBlue"] = "#191970"
    ImageMagickColorMap["navy"] = "#000080"
    ImageMagickColorMap["NavyBlue"] = "#000080"
    ImageMagickColorMap["RoyalBlue"] = "#4169E1"
    ImageMagickColorMap["RoyalBlue1"] = "#4876FF"
    ImageMagickColorMap["RoyalBlue2"] = "#436EEE"
    ImageMagickColorMap["RoyalBlue3"] = "#3A5FCD"
    ImageMagickColorMap["RoyalBlue4"] = "#27408B"
    ImageMagickColorMap["CornflowerBlue"] = "#6495ED"
    ImageMagickColorMap["LightSteelBlue"] = "#B0C4DE"
    ImageMagickColorMap["LightSteelBlue1"] = "#CAE1FF"
    ImageMagickColorMap["LightSteelBlue2"] = "#BCD2EE"
    ImageMagickColorMap["LightSteelBlue3"] = "#A2B5CD"
    ImageMagickColorMap["LightSteelBlue4"] = "#6E7B8B"
    ImageMagickColorMap["SlateGray4"] = "#6C7B8B"
    ImageMagickColorMap["SlateGray1"] = "#C6E2FF"
    ImageMagickColorMap["SlateGray2"] = "#B9D3EE"
    ImageMagickColorMap["SlateGray3"] = "#9FB6CD"
    ImageMagickColorMap["LightSlateGray"] = "#778899"
    ImageMagickColorMap["LightSlateGrey"] = "#778899"
    ImageMagickColorMap["SlateGray"] = "#708090"
    ImageMagickColorMap["SlateGrey"] = "#708090"
    ImageMagickColorMap["DodgerBlue"] = "#1E90FF"
    ImageMagickColorMap["DodgerBlue1"] = "#1E90FF"
    ImageMagickColorMap["DodgerBlue2"] = "#1C86EE"
    ImageMagickColorMap["DodgerBlue4"] = "#104E8B"
    ImageMagickColorMap["DodgerBlue3"] = "#1874CD"
    ImageMagickColorMap["AliceBlue"] = "#F0F8FF"
    ImageMagickColorMap["SteelBlue4"] = "#36648B"
    ImageMagickColorMap["SteelBlue"] = "#4682B4"
    ImageMagickColorMap["SteelBlue1"] = "#63B8FF"
    ImageMagickColorMap["SteelBlue2"] = "#5CACEE"
    ImageMagickColorMap["SteelBlue3"] = "#4F94CD"
    ImageMagickColorMap["SkyBlue4"] = "#4A708B"
    ImageMagickColorMap["SkyBlue1"] = "#87CEFF"
    ImageMagickColorMap["SkyBlue2"] = "#7EC0EE"
    ImageMagickColorMap["SkyBlue3"] = "#6CA6CD"
    ImageMagickColorMap["LightSkyBlue"] = "#87CEFA"
    ImageMagickColorMap["LightSkyBlue4"] = "#607B8B"
    ImageMagickColorMap["LightSkyBlue1"] = "#B0E2FF"
    ImageMagickColorMap["LightSkyBlue2"] = "#A4D3EE"
    ImageMagickColorMap["LightSkyBlue3"] = "#8DB6CD"
    ImageMagickColorMap["SkyBlue"] = "#87CEEB"
    ImageMagickColorMap["LightBlue3"] = "#9AC0CD"
    ImageMagickColorMap["DeepSkyBlue"] = "#00BFFF"
    ImageMagickColorMap["DeepSkyBlue1"] = "#00BFFF"
    ImageMagickColorMap["DeepSkyBlue2"] = "#00B2EE"
    ImageMagickColorMap["DeepSkyBlue4"] = "#00688B"
    ImageMagickColorMap["DeepSkyBlue3"] = "#009ACD"
    ImageMagickColorMap["LightBlue1"] = "#BFEFFF"
    ImageMagickColorMap["LightBlue2"] = "#B2DFEE"
    ImageMagickColorMap["LightBlue"] = "#ADD8E6"
    ImageMagickColorMap["LightBlue4"] = "#68838B"
    ImageMagickColorMap["PowderBlue"] = "#B0E0E6"
    ImageMagickColorMap["CadetBlue1"] = "#98F5FF"
    ImageMagickColorMap["CadetBlue2"] = "#8EE5EE"
    ImageMagickColorMap["CadetBlue3"] = "#7AC5CD"
    ImageMagickColorMap["CadetBlue4"] = "#53868B"
    ImageMagickColorMap["turquoise1"] = "#00F5FF"
    ImageMagickColorMap["turquoise2"] = "#00E5EE"
    ImageMagickColorMap["turquoise3"] = "#00C5CD"
    ImageMagickColorMap["turquoise4"] = "#00868B"
    ImageMagickColorMap["CadetBlue"] = "#5F9EA0"
    ImageMagickColorMap["DarkTurquoise"] = "#00CED1"
    ImageMagickColorMap["azure"] = "#F0FFFF"
    ImageMagickColorMap["azure1"] = "#F0FFFF"
    ImageMagickColorMap["LightCyan"] = "#E0FFFF"
    ImageMagickColorMap["LightCyan1"] = "#E0FFFF"
    ImageMagickColorMap["azure2"] = "#E0EEEE"
    ImageMagickColorMap["LightCyan2"] = "#D1EEEE"
    ImageMagickColorMap["PaleTurquoise1"] = "#BBFFFF"
    ImageMagickColorMap["PaleTurquoise"] = "#AFEEEE"
    ImageMagickColorMap["PaleTurquoise2"] = "#AEEEEE"
    ImageMagickColorMap["DarkSlateGray1"] = "#97FFFF"
    ImageMagickColorMap["azure3"] = "#C1CDCD"
    ImageMagickColorMap["LightCyan3"] = "#B4CDCD"
    ImageMagickColorMap["DarkSlateGray2"] = "#8DEEEE"
    ImageMagickColorMap["PaleTurquoise3"] = "#96CDCD"
    ImageMagickColorMap["DarkSlateGray3"] = "#79CDCD"
    ImageMagickColorMap["azure4"] = "#838B8B"
    ImageMagickColorMap["LightCyan4"] = "#7A8B8B"
    ImageMagickColorMap["aqua"] = "#00FFFF"
    ImageMagickColorMap["cyan"] = "#00FFFF"
    ImageMagickColorMap["cyan1"] = "#00FFFF"
    ImageMagickColorMap["PaleTurquoise4"] = "#668B8B"
    ImageMagickColorMap["cyan2"] = "#00EEEE"
    ImageMagickColorMap["DarkSlateGray4"] = "#528B8B"
    ImageMagickColorMap["cyan3"] = "#00CDCD"
    ImageMagickColorMap["cyan4"] = "#008B8B"
    ImageMagickColorMap["DarkCyan"] = "#008B8B"
    ImageMagickColorMap["teal"] = "#008080"
    ImageMagickColorMap["DarkSlateGray"] = "#2F4F4F"
    ImageMagickColorMap["DarkSlateGrey"] = "#2F4F4F"
    ImageMagickColorMap["MediumTurquoise"] = "#48D1CC"
    ImageMagickColorMap["LightSeaGreen"] = "#20B2AA"
    ImageMagickColorMap["turquoise"] = "#40E0D0"
    ImageMagickColorMap["aquamarine4"] = "#458B74"
    ImageMagickColorMap["aquamarine"] = "#7FFFD4"
    ImageMagickColorMap["aquamarine1"] = "#7FFFD4"
    ImageMagickColorMap["aquamarine2"] = "#76EEC6"
    ImageMagickColorMap["aquamarine3"] = "#66CDAA"
    ImageMagickColorMap["MediumAquamarine"] = "#66CDAA"
    ImageMagickColorMap["MediumSpringGreen"] = "#00FA9A"
    ImageMagickColorMap["MintCream"] = "#F5FFFA"
    ImageMagickColorMap["SpringGreen"] = "#00FF7F"
    ImageMagickColorMap["SpringGreen1"] = "#00FF7F"
    ImageMagickColorMap["SpringGreen2"] = "#00EE76"
    ImageMagickColorMap["SpringGreen3"] = "#00CD66"
    ImageMagickColorMap["SpringGreen4"] = "#008B45"
    ImageMagickColorMap["MediumSeaGreen"] = "#3CB371"
    ImageMagickColorMap["SeaGreen"] = "#2E8B57"
    ImageMagickColorMap["SeaGreen3"] = "#43CD80"
    ImageMagickColorMap["SeaGreen1"] = "#54FF9F"
    ImageMagickColorMap["SeaGreen4"] = "#2E8B57"
    ImageMagickColorMap["SeaGreen2"] = "#4EEE94"
    ImageMagickColorMap["MediumForestGreen"] = "#32814B"
    ImageMagickColorMap["honeydew"] = "#F0FFF0"
    ImageMagickColorMap["honeydew1"] = "#F0FFF0"
    ImageMagickColorMap["honeydew2"] = "#E0EEE0"
    ImageMagickColorMap["DarkSeaGreen1"] = "#C1FFC1"
    ImageMagickColorMap["DarkSeaGreen2"] = "#B4EEB4"
    ImageMagickColorMap["PaleGreen1"] = "#9AFF9A"
    ImageMagickColorMap["PaleGreen"] = "#98FB98"
    ImageMagickColorMap["honeydew3"] = "#C1CDC1"
    ImageMagickColorMap["LightGreen"] = "#90EE90"
    ImageMagickColorMap["PaleGreen2"] = "#90EE90"
    ImageMagickColorMap["DarkSeaGreen3"] = "#9BCD9B"
    ImageMagickColorMap["DarkSeaGreen"] = "#8FBC8F"
    ImageMagickColorMap["PaleGreen3"] = "#7CCD7C"
    ImageMagickColorMap["honeydew4"] = "#838B83"
    ImageMagickColorMap["green1"] = "#00FF00"
    ImageMagickColorMap["lime"] = "#00FF00"
    ImageMagickColorMap["LimeGreen"] = "#32CD32"
    ImageMagickColorMap["DarkSeaGreen4"] = "#698B69"
    ImageMagickColorMap["green2"] = "#00EE00"
    ImageMagickColorMap["PaleGreen4"] = "#548B54"
    ImageMagickColorMap["green3"] = "#00CD00"
    ImageMagickColorMap["ForestGreen"] = "#228B22"
    ImageMagickColorMap["green4"] = "#008B00"
    ImageMagickColorMap["green"] = "#008000"
    ImageMagickColorMap["DarkGreen"] = "#006400"
    ImageMagickColorMap["LawnGreen"] = "#7CFC00"
    ImageMagickColorMap["chartreuse"] = "#7FFF00"
    ImageMagickColorMap["chartreuse1"] = "#7FFF00"
    ImageMagickColorMap["chartreuse2"] = "#76EE00"
    ImageMagickColorMap["chartreuse3"] = "#66CD00"
    ImageMagickColorMap["chartreuse4"] = "#458B00"
    ImageMagickColorMap["GreenYellow"] = "#ADFF2F"
    ImageMagickColorMap["DarkOliveGreen3"] = "#A2CD5A"
    ImageMagickColorMap["DarkOliveGreen1"] = "#CAFF70"
    ImageMagickColorMap["DarkOliveGreen2"] = "#BCEE68"
    ImageMagickColorMap["DarkOliveGreen4"] = "#6E8B3D"
    ImageMagickColorMap["DarkOliveGreen"] = "#556B2F"
    ImageMagickColorMap["OliveDrab"] = "#6B8E23"
    ImageMagickColorMap["OliveDrab1"] = "#C0FF3E"
    ImageMagickColorMap["OliveDrab2"] = "#B3EE3A"
    ImageMagickColorMap["OliveDrab3"] = "#9ACD32"
    ImageMagickColorMap["YellowGreen"] = "#9ACD32"
    ImageMagickColorMap["OliveDrab4"] = "#698B22"
    ImageMagickColorMap["ivory"] = "#FFFFF0"
    ImageMagickColorMap["ivory1"] = "#FFFFF0"
    ImageMagickColorMap["LightYellow"] = "#FFFFE0"
    ImageMagickColorMap["LightYellow1"] = "#FFFFE0"
    ImageMagickColorMap["beige"] = "#F5F5DC"
    ImageMagickColorMap["ivory2"] = "#EEEEE0"
    ImageMagickColorMap["LightGoldenrodYellow"] = "#FAFAD2"
    ImageMagickColorMap["LightYellow2"] = "#EEEED1"
    ImageMagickColorMap["ivory3"] = "#CDCDC1"
    ImageMagickColorMap["LightYellow3"] = "#CDCDB4"
    ImageMagickColorMap["ivory4"] = "#8B8B83"
    ImageMagickColorMap["LightYellow4"] = "#8B8B7A"
    ImageMagickColorMap["yellow"] = "#FFFF00"
    ImageMagickColorMap["yellow1"] = "#FFFF00"
    ImageMagickColorMap["yellow2"] = "#EEEE00"
    ImageMagickColorMap["yellow3"] = "#CDCD00"
    ImageMagickColorMap["yellow4"] = "#8B8B00"
    ImageMagickColorMap["olive"] = "#808000"
    ImageMagickColorMap["DarkKhaki"] = "#BDB76B"
    ImageMagickColorMap["khaki2"] = "#EEE685"
    ImageMagickColorMap["LemonChiffon4"] = "#8B8970"
    ImageMagickColorMap["khaki1"] = "#FFF68F"
    ImageMagickColorMap["khaki3"] = "#CDC673"
    ImageMagickColorMap["khaki4"] = "#8B864E"
    ImageMagickColorMap["PaleGoldenrod"] = "#EEE8AA"
    ImageMagickColorMap["LemonChiffon"] = "#FFFACD"
    ImageMagickColorMap["LemonChiffon1"] = "#FFFACD"
    ImageMagickColorMap["khaki"] = "#F0E68C"
    ImageMagickColorMap["LemonChiffon3"] = "#CDC9A5"
    ImageMagickColorMap["LemonChiffon2"] = "#EEE9BF"
    ImageMagickColorMap["MediumGoldenRod"] = "#D1C166"
    ImageMagickColorMap["cornsilk4"] = "#8B8878"
    ImageMagickColorMap["gold"] = "#FFD700"
    ImageMagickColorMap["gold1"] = "#FFD700"
    ImageMagickColorMap["gold2"] = "#EEC900"
    ImageMagickColorMap["gold3"] = "#CDAD00"
    ImageMagickColorMap["gold4"] = "#8B7500"
    ImageMagickColorMap["LightGoldenrod"] = "#EEDD82"
    ImageMagickColorMap["LightGoldenrod4"] = "#8B814C"
    ImageMagickColorMap["LightGoldenrod1"] = "#FFEC8B"
    ImageMagickColorMap["LightGoldenrod3"] = "#CDBE70"
    ImageMagickColorMap["LightGoldenrod2"] = "#EEDC82"
    ImageMagickColorMap["cornsilk3"] = "#CDC8B1"
    ImageMagickColorMap["cornsilk2"] = "#EEE8CD"
    ImageMagickColorMap["cornsilk"] = "#FFF8DC"
    ImageMagickColorMap["cornsilk1"] = "#FFF8DC"
    ImageMagickColorMap["goldenrod"] = "#DAA520"
    ImageMagickColorMap["goldenrod1"] = "#FFC125"
    ImageMagickColorMap["goldenrod2"] = "#EEB422"
    ImageMagickColorMap["goldenrod3"] = "#CD9B1D"
    ImageMagickColorMap["goldenrod4"] = "#8B6914"
    ImageMagickColorMap["DarkGoldenrod"] = "#B8860B"
    ImageMagickColorMap["DarkGoldenrod1"] = "#FFB90F"
    ImageMagickColorMap["DarkGoldenrod2"] = "#EEAD0E"
    ImageMagickColorMap["DarkGoldenrod3"] = "#CD950C"
    ImageMagickColorMap["DarkGoldenrod4"] = "#8B6508"
    ImageMagickColorMap["FloralWhite"] = "#FFFAF0"
    ImageMagickColorMap["wheat2"] = "#EED8AE"
    ImageMagickColorMap["OldLace"] = "#FDF5E6"
    ImageMagickColorMap["wheat"] = "#F5DEB3"
    ImageMagickColorMap["wheat1"] = "#FFE7BA"
    ImageMagickColorMap["wheat3"] = "#CDBA96"
    ImageMagickColorMap["orange"] = "#FFA500"
    ImageMagickColorMap["orange1"] = "#FFA500"
    ImageMagickColorMap["orange2"] = "#EE9A00"
    ImageMagickColorMap["orange3"] = "#CD8500"
    ImageMagickColorMap["orange4"] = "#8B5A00"
    ImageMagickColorMap["wheat4"] = "#8B7E66"
    ImageMagickColorMap["moccasin"] = "#FFE4B5"
    ImageMagickColorMap["PapayaWhip"] = "#FFEFD5"
    ImageMagickColorMap["NavajoWhite3"] = "#CDB38B"
    ImageMagickColorMap["BlanchedAlmond"] = "#FFEBCD"
    ImageMagickColorMap["NavajoWhite"] = "#FFDEAD"
    ImageMagickColorMap["NavajoWhite1"] = "#FFDEAD"
    ImageMagickColorMap["NavajoWhite2"] = "#EECFA1"
    ImageMagickColorMap["NavajoWhite4"] = "#8B795E"
    ImageMagickColorMap["AntiqueWhite4"] = "#8B8378"
    ImageMagickColorMap["AntiqueWhite"] = "#FAEBD7"
    ImageMagickColorMap["tan"] = "#D2B48C"
    ImageMagickColorMap["bisque4"] = "#8B7D6B"
    ImageMagickColorMap["burlywood"] = "#DEB887"
    ImageMagickColorMap["AntiqueWhite2"] = "#EEDFCC"
    ImageMagickColorMap["burlywood1"] = "#FFD39B"
    ImageMagickColorMap["burlywood3"] = "#CDAA7D"
    ImageMagickColorMap["burlywood2"] = "#EEC591"
    ImageMagickColorMap["AntiqueWhite1"] = "#FFEFDB"
    ImageMagickColorMap["burlywood4"] = "#8B7355"
    ImageMagickColorMap["AntiqueWhite3"] = "#CDC0B0"
    ImageMagickColorMap["DarkOrange"] = "#FF8C00"
    ImageMagickColorMap["bisque2"] = "#EED5B7"
    ImageMagickColorMap["bisque"] = "#FFE4C4"
    ImageMagickColorMap["bisque1"] = "#FFE4C4"
    ImageMagickColorMap["bisque3"] = "#CDB79E"
    ImageMagickColorMap["DarkOrange1"] = "#FF7F00"
    ImageMagickColorMap["linen"] = "#FAF0E6"
    ImageMagickColorMap["DarkOrange2"] = "#EE7600"
    ImageMagickColorMap["DarkOrange3"] = "#CD6600"
    ImageMagickColorMap["DarkOrange4"] = "#8B4500"
    ImageMagickColorMap["peru"] = "#CD853F"
    ImageMagickColorMap["tan1"] = "#FFA54F"
    ImageMagickColorMap["tan2"] = "#EE9A49"
    ImageMagickColorMap["tan3"] = "#CD853F"
    ImageMagickColorMap["tan4"] = "#8B5A2B"
    ImageMagickColorMap["PeachPuff"] = "#FFDAB9"
    ImageMagickColorMap["PeachPuff1"] = "#FFDAB9"
    ImageMagickColorMap["PeachPuff4"] = "#8B7765"
    ImageMagickColorMap["PeachPuff2"] = "#EECBAD"
    ImageMagickColorMap["PeachPuff3"] = "#CDAF95"
    ImageMagickColorMap["SandyBrown"] = "#F4A460"
    ImageMagickColorMap["seashell4"] = "#8B8682"
    ImageMagickColorMap["seashell2"] = "#EEE5DE"
    ImageMagickColorMap["seashell3"] = "#CDC5BF"
    ImageMagickColorMap["chocolate"] = "#D2691E"
    ImageMagickColorMap["chocolate1"] = "#FF7F24"
    ImageMagickColorMap["chocolate2"] = "#EE7621"
    ImageMagickColorMap["chocolate3"] = "#CD661D"
    ImageMagickColorMap["chocolate4"] = "#8B4513"
    ImageMagickColorMap["SaddleBrown"] = "#8B4513"
    ImageMagickColorMap["seashell"] = "#FFF5EE"
    ImageMagickColorMap["seashell1"] = "#FFF5EE"
    ImageMagickColorMap["sienna4"] = "#8B4726"
    ImageMagickColorMap["sienna"] = "#A0522D"
    ImageMagickColorMap["sienna1"] = "#FF8247"
    ImageMagickColorMap["sienna2"] = "#EE7942"
    ImageMagickColorMap["sienna3"] = "#CD6839"
    ImageMagickColorMap["LightSalmon3"] = "#CD8162"
    ImageMagickColorMap["LightSalmon"] = "#FFA07A"
    ImageMagickColorMap["LightSalmon1"] = "#FFA07A"
    ImageMagickColorMap["LightSalmon4"] = "#8B5742"
    ImageMagickColorMap["LightSalmon2"] = "#EE9572"
    ImageMagickColorMap["coral"] = "#FF7F50"
    ImageMagickColorMap["OrangeRed"] = "#FF4500"
    ImageMagickColorMap["OrangeRed1"] = "#FF4500"
    ImageMagickColorMap["OrangeRed2"] = "#EE4000"
    ImageMagickColorMap["OrangeRed3"] = "#CD3700"
    ImageMagickColorMap["OrangeRed4"] = "#8B2500"
    ImageMagickColorMap["DarkSalmon"] = "#E9967A"
    ImageMagickColorMap["salmon1"] = "#FF8C69"
    ImageMagickColorMap["salmon2"] = "#EE8262"
    ImageMagickColorMap["salmon3"] = "#CD7054"
    ImageMagickColorMap["salmon4"] = "#8B4C39"
    ImageMagickColorMap["coral1"] = "#FF7256"
    ImageMagickColorMap["coral2"] = "#EE6A50"
    ImageMagickColorMap["coral3"] = "#CD5B45"
    ImageMagickColorMap["coral4"] = "#8B3E2F"
    ImageMagickColorMap["tomato4"] = "#8B3626"
    ImageMagickColorMap["tomato"] = "#FF6347"
    ImageMagickColorMap["tomato1"] = "#FF6347"
    ImageMagickColorMap["tomato2"] = "#EE5C42"
    ImageMagickColorMap["tomato3"] = "#CD4F39"
    ImageMagickColorMap["MistyRose4"] = "#8B7D7B"
    ImageMagickColorMap["MistyRose2"] = "#EED5D2"
    ImageMagickColorMap["MistyRose"] = "#FFE4E1"
    ImageMagickColorMap["MistyRose1"] = "#FFE4E1"
    ImageMagickColorMap["salmon"] = "#FA8072"
    ImageMagickColorMap["MistyRose3"] = "#CDB7B5"
    ImageMagickColorMap["white"] = "#FFFFFF"
    ImageMagickColorMap["gray100"] = "#FFFFFF"
    ImageMagickColorMap["grey100"] = "#FFFFFF"
    ImageMagickColorMap["grey100"] = "#FFFFFF"
    ImageMagickColorMap["gray99"] = "#FCFCFC"
    ImageMagickColorMap["grey99"] = "#FCFCFC"
    ImageMagickColorMap["gray98"] = "#FAFAFA"
    ImageMagickColorMap["grey98"] = "#FAFAFA"
    ImageMagickColorMap["gray97"] = "#F7F7F7"
    ImageMagickColorMap["grey97"] = "#F7F7F7"
    ImageMagickColorMap["gray96"] = "#F5F5F5"
    ImageMagickColorMap["grey96"] = "#F5F5F5"
    ImageMagickColorMap["WhiteSmoke"] = "#F5F5F5"
    ImageMagickColorMap["gray95"] = "#F2F2F2"
    ImageMagickColorMap["grey95"] = "#F2F2F2"
    ImageMagickColorMap["gray94"] = "#F0F0F0"
    ImageMagickColorMap["grey94"] = "#F0F0F0"
    ImageMagickColorMap["gray93"] = "#EDEDED"
    ImageMagickColorMap["grey93"] = "#EDEDED"
    ImageMagickColorMap["gray92"] = "#EBEBEB"
    ImageMagickColorMap["grey92"] = "#EBEBEB"
    ImageMagickColorMap["gray91"] = "#E8E8E8"
    ImageMagickColorMap["grey91"] = "#E8E8E8"
    ImageMagickColorMap["gray90"] = "#E5E5E5"
    ImageMagickColorMap["grey90"] = "#E5E5E5"
    ImageMagickColorMap["gray89"] = "#E3E3E3"
    ImageMagickColorMap["grey89"] = "#E3E3E3"
    ImageMagickColorMap["gray88"] = "#E0E0E0"
    ImageMagickColorMap["grey88"] = "#E0E0E0"
    ImageMagickColorMap["gray87"] = "#DEDEDE"
    ImageMagickColorMap["grey87"] = "#DEDEDE"
    ImageMagickColorMap["gainsboro"] = "#DCDCDC"
    ImageMagickColorMap["gray86"] = "#DBDBDB"
    ImageMagickColorMap["grey86"] = "#DBDBDB"
    ImageMagickColorMap["gray85"] = "#D9D9D9"
    ImageMagickColorMap["grey85"] = "#D9D9D9"
    ImageMagickColorMap["gray84"] = "#D6D6D6"
    ImageMagickColorMap["grey84"] = "#D6D6D6"
    ImageMagickColorMap["gray83"] = "#D4D4D4"
    ImageMagickColorMap["grey83"] = "#D4D4D4"
    ImageMagickColorMap["LightGray"] = "#D3D3D3"
    ImageMagickColorMap["LightGrey"] = "#D3D3D3"
    ImageMagickColorMap["gray82"] = "#D1D1D1"
    ImageMagickColorMap["grey82"] = "#D1D1D1"
    ImageMagickColorMap["gray81"] = "#CFCFCF"
    ImageMagickColorMap["grey81"] = "#CFCFCF"
    ImageMagickColorMap["gray80"] = "#CCCCCC"
    ImageMagickColorMap["grey80"] = "#CCCCCC"
    ImageMagickColorMap["gray79"] = "#C9C9C9"
    ImageMagickColorMap["grey79"] = "#C9C9C9"
    ImageMagickColorMap["gray78"] = "#C7C7C7"
    ImageMagickColorMap["grey78"] = "#C7C7C7"
    ImageMagickColorMap["gray77"] = "#C4C4C4"
    ImageMagickColorMap["grey77"] = "#C4C4C4"
    ImageMagickColorMap["gray76"] = "#C2C2C2"
    ImageMagickColorMap["grey76"] = "#C2C2C2"
    ImageMagickColorMap["silver"] = "#C0C0C0"
    ImageMagickColorMap["gray75"] = "#BFBFBF"
    ImageMagickColorMap["grey75"] = "#BFBFBF"
    ImageMagickColorMap["gray74"] = "#BDBDBD"
    ImageMagickColorMap["grey74"] = "#BDBDBD"
    ImageMagickColorMap["gray73"] = "#BABABA"
    ImageMagickColorMap["grey73"] = "#BABABA"
    ImageMagickColorMap["gray72"] = "#B8B8B8"
    ImageMagickColorMap["grey72"] = "#B8B8B8"
    ImageMagickColorMap["gray71"] = "#B5B5B5"
    ImageMagickColorMap["grey71"] = "#B5B5B5"
    ImageMagickColorMap["gray70"] = "#B3B3B3"
    ImageMagickColorMap["grey70"] = "#B3B3B3"
    ImageMagickColorMap["gray69"] = "#B0B0B0"
    ImageMagickColorMap["grey69"] = "#B0B0B0"
    ImageMagickColorMap["gray68"] = "#ADADAD"
    ImageMagickColorMap["grey68"] = "#ADADAD"
    ImageMagickColorMap["gray67"] = "#ABABAB"
    ImageMagickColorMap["grey67"] = "#ABABAB"
    ImageMagickColorMap["DarkGray"] = "#A9A9A9"
    ImageMagickColorMap["DarkGrey"] = "#A9A9A9"
    ImageMagickColorMap["gray66"] = "#A8A8A8"
    ImageMagickColorMap["grey66"] = "#A8A8A8"
    ImageMagickColorMap["gray65"] = "#A6A6A6"
    ImageMagickColorMap["grey65"] = "#A6A6A6"
    ImageMagickColorMap["gray64"] = "#A3A3A3"
    ImageMagickColorMap["grey64"] = "#A3A3A3"
    ImageMagickColorMap["gray63"] = "#A1A1A1"
    ImageMagickColorMap["grey63"] = "#A1A1A1"
    ImageMagickColorMap["gray62"] = "#9E9E9E"
    ImageMagickColorMap["grey62"] = "#9E9E9E"
    ImageMagickColorMap["gray61"] = "#9C9C9C"
    ImageMagickColorMap["grey61"] = "#9C9C9C"
    ImageMagickColorMap["gray60"] = "#999999"
    ImageMagickColorMap["grey60"] = "#999999"
    ImageMagickColorMap["gray59"] = "#969696"
    ImageMagickColorMap["grey59"] = "#969696"
    ImageMagickColorMap["gray58"] = "#949494"
    ImageMagickColorMap["grey58"] = "#949494"
    ImageMagickColorMap["gray57"] = "#919191"
    ImageMagickColorMap["grey57"] = "#919191"
    ImageMagickColorMap["gray56"] = "#8F8F8F"
    ImageMagickColorMap["grey56"] = "#8F8F8F"
    ImageMagickColorMap["gray55"] = "#8C8C8C"
    ImageMagickColorMap["grey55"] = "#8C8C8C"
    ImageMagickColorMap["gray54"] = "#8A8A8A"
    ImageMagickColorMap["grey54"] = "#8A8A8A"
    ImageMagickColorMap["gray53"] = "#878787"
    ImageMagickColorMap["grey53"] = "#878787"
    ImageMagickColorMap["gray52"] = "#858585"
    ImageMagickColorMap["grey52"] = "#858585"
    ImageMagickColorMap["gray51"] = "#828282"
    ImageMagickColorMap["grey51"] = "#828282"
    ImageMagickColorMap["fractal"] = "#808080"
    ImageMagickColorMap["gray50"] = "#7F7F7F"
    ImageMagickColorMap["grey50"] = "#7F7F7F"
    ImageMagickColorMap["gray"] = "#7E7E7E"
    ImageMagickColorMap["gray49"] = "#7D7D7D"
    ImageMagickColorMap["grey49"] = "#7D7D7D"
    ImageMagickColorMap["gray48"] = "#7A7A7A"
    ImageMagickColorMap["grey48"] = "#7A7A7A"
    ImageMagickColorMap["gray47"] = "#787878"
    ImageMagickColorMap["grey47"] = "#787878"
    ImageMagickColorMap["gray46"] = "#757575"
    ImageMagickColorMap["grey46"] = "#757575"
    ImageMagickColorMap["gray45"] = "#737373"
    ImageMagickColorMap["grey45"] = "#737373"
    ImageMagickColorMap["gray44"] = "#707070"
    ImageMagickColorMap["grey44"] = "#707070"
    ImageMagickColorMap["gray43"] = "#6E6E6E"
    ImageMagickColorMap["grey43"] = "#6E6E6E"
    ImageMagickColorMap["gray42"] = "#6B6B6B"
    ImageMagickColorMap["grey42"] = "#6B6B6B"
    ImageMagickColorMap["DimGray"] = "#696969"
    ImageMagickColorMap["DimGrey"] = "#696969"
    ImageMagickColorMap["gray41"] = "#696969"
    ImageMagickColorMap["grey41"] = "#696969"
    ImageMagickColorMap["gray40"] = "#666666"
    ImageMagickColorMap["grey40"] = "#666666"
    ImageMagickColorMap["gray39"] = "#636363"
    ImageMagickColorMap["grey39"] = "#636363"
    ImageMagickColorMap["gray38"] = "#616161"
    ImageMagickColorMap["grey38"] = "#616161"
    ImageMagickColorMap["gray37"] = "#5E5E5E"
    ImageMagickColorMap["grey37"] = "#5E5E5E"
    ImageMagickColorMap["gray36"] = "#5C5C5C"
    ImageMagickColorMap["grey36"] = "#5C5C5C"
    ImageMagickColorMap["gray35"] = "#595959"
    ImageMagickColorMap["grey35"] = "#595959"
    ImageMagickColorMap["gray34"] = "#575757"
    ImageMagickColorMap["grey34"] = "#575757"
    ImageMagickColorMap["gray33"] = "#545454"
    ImageMagickColorMap["grey33"] = "#545454"
    ImageMagickColorMap["gray32"] = "#525252"
    ImageMagickColorMap["grey32"] = "#525252"
    ImageMagickColorMap["gray31"] = "#4F4F4F"
    ImageMagickColorMap["grey31"] = "#4F4F4F"
    ImageMagickColorMap["gray30"] = "#4D4D4D"
    ImageMagickColorMap["grey30"] = "#4D4D4D"
    ImageMagickColorMap["gray29"] = "#4A4A4A"
    ImageMagickColorMap["grey29"] = "#4A4A4A"
    ImageMagickColorMap["gray28"] = "#474747"
    ImageMagickColorMap["grey28"] = "#474747"
    ImageMagickColorMap["gray27"] = "#454545"
    ImageMagickColorMap["grey27"] = "#454545"
    ImageMagickColorMap["gray26"] = "#424242"
    ImageMagickColorMap["grey26"] = "#424242"
    ImageMagickColorMap["gray25"] = "#404040"
    ImageMagickColorMap["grey25"] = "#404040"
    ImageMagickColorMap["gray24"] = "#3D3D3D"
    ImageMagickColorMap["grey24"] = "#3D3D3D"
    ImageMagickColorMap["gray23"] = "#3B3B3B"
    ImageMagickColorMap["grey23"] = "#3B3B3B"
    ImageMagickColorMap["gray22"] = "#383838"
    ImageMagickColorMap["grey22"] = "#383838"
    ImageMagickColorMap["gray21"] = "#363636"
    ImageMagickColorMap["grey21"] = "#363636"
    ImageMagickColorMap["gray20"] = "#333333"
    ImageMagickColorMap["grey20"] = "#333333"
    ImageMagickColorMap["gray19"] = "#303030"
    ImageMagickColorMap["grey19"] = "#303030"
    ImageMagickColorMap["gray18"] = "#2E2E2E"
    ImageMagickColorMap["grey18"] = "#2E2E2E"
    ImageMagickColorMap["gray17"] = "#2B2B2B"
    ImageMagickColorMap["grey17"] = "#2B2B2B"
    ImageMagickColorMap["gray16"] = "#292929"
    ImageMagickColorMap["grey16"] = "#292929"
    ImageMagickColorMap["gray15"] = "#262626"
    ImageMagickColorMap["grey15"] = "#262626"
    ImageMagickColorMap["gray14"] = "#242424"
    ImageMagickColorMap["grey14"] = "#242424"
    ImageMagickColorMap["gray13"] = "#212121"
    ImageMagickColorMap["grey13"] = "#212121"
    ImageMagickColorMap["gray12"] = "#1F1F1F"
    ImageMagickColorMap["grey12"] = "#1F1F1F"
    ImageMagickColorMap["gray11"] = "#1C1C1C"
    ImageMagickColorMap["grey11"] = "#1C1C1C"
    ImageMagickColorMap["gray10"] = "#1A1A1A"
    ImageMagickColorMap["grey10"] = "#1A1A1A"
    ImageMagickColorMap["gray9"] = "#171717"
    ImageMagickColorMap["grey9"] = "#171717"
    ImageMagickColorMap["gray8"] = "#141414"
    ImageMagickColorMap["grey8"] = "#141414"
    ImageMagickColorMap["gray7"] = "#121212"
    ImageMagickColorMap["grey7"] = "#121212"
    ImageMagickColorMap["gray6"] = "#0F0F0F"
    ImageMagickColorMap["grey6"] = "#0F0F0F"
    ImageMagickColorMap["gray5"] = "#0D0D0D"
    ImageMagickColorMap["grey5"] = "#0D0D0D"
    ImageMagickColorMap["gray4"] = "#0A0A0A"
    ImageMagickColorMap["grey4"] = "#0A0A0A"
    ImageMagickColorMap["gray3"] = "#080808"
    ImageMagickColorMap["grey3"] = "#080808"
    ImageMagickColorMap["gray2"] = "#050505"
    ImageMagickColorMap["grey2"] = "#050505"
    ImageMagickColorMap["gray1"] = "#030303"
    ImageMagickColorMap["grey1"] = "#030303"
    ImageMagickColorMap["black"] = "#000000"
    ImageMagickColorMap["gray0"] = "#000000"
    ImageMagickColorMap["grey0"] = "#000000"
    ImageMagickColorMap["opaque"] = "#000000"
    
    @staticmethod
    def rgbFromStr(s):
        # s starts with a #.
        r, g, b = int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16)
        return r, g, b
    
    @staticmethod
    def findNearestWebColorName(xxx_todo_changeme):
        (R, G, B) = xxx_todo_changeme
        return ColorNames.findNearestColorName((R, G, B), ColorNames.WebColorMap)
    
    @staticmethod
    def findNearestImageMagickColorName(xxx_todo_changeme1):
        (R, G, B) = xxx_todo_changeme1
        return ColorNames.findNearestColorName((R, G, B), ColorNames.ImageMagickColorMap)
    
    @staticmethod
    def findNearestColorName(xxx_todo_changeme2, Map):
        (R, G, B) = xxx_todo_changeme2
        mindiff = None
        mincolorname = None
        for d in Map:
            r, g, b = ColorNames.rgbFromStr(Map[d])
            diff = abs(R - r) * 256 + abs(G - g) * 256 + abs(B - b) * 256
            if mindiff is None or diff < mindiff:
                mindiff = diff
                mincolorname = d
        return mincolorname

# endregion
