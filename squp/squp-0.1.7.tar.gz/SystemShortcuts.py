'''
SystemShortcuts.py
Provides all of the system shortcuts used throughout the classes of the Squarespace Uploader program
'''

# ---------------------- BEGIN IMPORTS ----------------------

from information import Info
import time, re, json, urllib.request, urllib.parse, urllib.error, unicodedata, random


# ----------------------- END IMPORTS -----------------------

# ---------------- BEGIN SHORTCUT METHODS -------------------

### Enables for shortening of making the program sleep
# Tells the program to sleep for the specified amount of time
# Python used Rest!
def slp(tim=0.5):
    time.sleep(tim)


# Sleeps for 0.5 seconds
def slp2():
    time.sleep(.5)


# Sleeps for 0.3 seconds
def slp3():
    time.sleep(.3)


# Returns whether the string is numeric or not
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# Method that determines a url based on keywords
def get_admin_url(keywords):
    # If no keyword is given at all, go to store page
    if len(keywords) == 0:
        return Info.STORE_PAGE
    # However, if something is given, figure out what to give back
    # Basic Filename (keyword) input
    elif 'Inventory2' or 'inventory2' or 'Inventory 2' or 'inventory 2' in [x for x in [y for y in keywords]]:
        return Info.INVENTORY_PAGE_Spring_2017
    elif 'Inventory' or 'inventory' in [x for x in [y for y in keywords]]:
        return Info.INVENTORY_PAGE
    # Direct URL input, assuming only one given
    elif 'http' in keywords[0]:
        return keywords[0]
    # Default all other cases (errors) to less important page
    else:
        return Info.TESTING_PAGE


# Similar to above, returns the json format of the page indicated by the keyword
def get_json_url(keywords):
    # If no keyword is given at all, go to store page
    if len(keywords) == 0:
        return 'https://www.lionelsmithltd.com/shop?format=json-pretty'
    # However, if something is given, figure out what to give back
    # Basic Filename (keyword) input
    elif 'Inventory' or 'inventory' in [x for x in [y for y in keywords]]:
        return 'https://www.lionelsmithltd.com/shop-more?format=json-pretty'
    # If it's a direct url input, get it from the last parameter in the given keys
    elif 'http' in keywords[-1]:
        return keywords[-1]
    # Default all other cases (errors) to main page since it's good data that can't be modified
    else:
        return 'https://www.lionelsmithltd.com/shop?format=json-pretty'


# Returns a random entry from the funny loading quotes
def get_loading_message():
    # Define the messages
    messages = Info.messages
    # Return the message at that index
    return random.choice(messages)


# ----------------- END SHORTCUT METHODS --------------------

# ----------------- BEGIN COMPARE METHODS -------------------

# A very basic comparison of two lists
def compare(list1, list2):
    # Removes empty items from the first list
    for l in reversed(list1):
        if len(l) == 0 or l is None or l == '':
            list1.remove(l)
    # Removes empty items from the second list
    for l in reversed(list2):
        if len(l) == 0 or l is None or l == '':
            list2.remove(l)
    # Returns the comparison of the new lists
    return sorted(list1) == sorted(list2) and len(list1) == len(list2)


# List 1 is hopefully the smaller of the two
def compare_imgs(list1, list2):
    # Duplicate list variables for temporary use
    d1 = []
    d2 = []
    update = False
    # Copy over the relevant parts of each filename from both lists
    for l in list1:
        d1.append(l[0:13].lower())
    for l in list2:
        d2.append(l.split('/')[-1][0:13].lower())
    # No need to check the first list here, it's assumed that it's the list from the current database, and must have at least one file (for now)
    if len(d2) != 0:
        for l in d1:
            # If it's not in the other list, mark it as such and move on
            if l not in d2:
                print('Update Needed')
                update = True
                # Python used Brick Break!
                break
    return update


# Replaces first-person pronouns to accredit sellers properly
def other_people(replaced, origin='Southern Tide'):
    if replaced is not None:
        r = " ".join(replaced) if type(replaced) is list else replaced
        r.encode('ascii', 'xmlcharrefreplace')
        o = str(origin)
        if "(u'" in o:
            o = o.split("'")[1]
        woST = re.sub(r"\b", "", r)
        woST = re.sub(r"\.\b", "", woST)
        woST = re.sub(r"(?i)^We.*ve\sgot", o + " has", woST)
        woST = re.sub(r"(?i)\sWe.*ve\sgot", " " + o + " has", woST)
        woST = re.sub(r"(?i)^we.*ve", o + " has", woST)
        woST = re.sub(r"(?i)\swe.*ve", " " + o + " has", woST)
        woST = re.sub(r"(?i)^we\s", o + " has ", woST)
        woST = re.sub(r"(?i)\swe\s", " " + o + " has ", woST)
        woST = re.sub(r"(?i)^our\s", o + "'s ", woST)
        woST = re.sub(r"(?i)\sour\s", " " + o + "'s ", woST)
        return woST
    else:
        return replaced