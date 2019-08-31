# -*- coding: utf-8 -*-
'''
SplinterShortcuts.py
Provides all of the shortcut methods used throughout the classes of the Squarespace Uploader (interface.py) program
'''

# ---------------------- BEGIN IMPORTS ----------------------

import re
from splinter import Browser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import SystemShortcuts as SyS
from information import Info

# ----------------------- END IMPORTS -----------------------

# -------------- BEGIN VARIABLE DECLARATION -----------------

# region Globals

# Declare the browser that will be used, set as nothing until initialized
browser = None


# Method that will set the browser that will be known globally throughout this class
def set_browser(b):
    global browser
    browser = b


# Declare the browser that will be used, set as nothing until initialized
logged_in = False


# Method that will set the browser that will be known globally throughout this class
def set_logged_in(l):
    global logged_in
    loggedIn = l


# endregion

# --------------- END VARIABLE DECLARATION ------------------

# ---------------- BEGIN SHORTCUT METHODS -------------------

# region Shortcuts

### Literal Keyboard Shortcut methods
# Sends the CTRL + A shortcut to the designated element
def send_select_all(element):
    global browser
    selectAll = ActionChains(browser.driver)
    selectAll.send_keys(Keys.CONTROL + 'a')
    element.click()
    selectAll.perform()


# Sends the CTRL + A shortcut to the designated element, and then hits backspace to delete everything
def select_all_and_erase(element):
    global browser
    # Select everything
    # element.click()
    selectAll = ActionChains(browser.driver)
    selectAll.send_keys(Keys.CONTROL + 'a')
    selectAll.perform()
    # Delete everything
    try:
        # Try using the splinter implementation
        element.type(Keys.BACK_SPACE)
    # It wasn't very effective...
    except:
        # If that doesn't work, use the selenium implementation, or nothing at all
        try:
            element.send_keys(Keys.BACK_SPACE)
        # It wasn't very effective
        except:
            pass


# Saves and closes the current element
def save_and_close():
    move_and_click(css('input.saveAndClose'))
    # Python used Rest!
    SyS.slp(1.5)


# Runs a script inside the browser, given as a string (kept camelCase to avoid possible conflicts)
def runScript(script, element):
    global browser
    browser.driver.execute_script(script, element)


# Simple log in method for when the browser is already on the login page
def simple_login():
    global browser
    browser.fill('email', Info.LOGIN)
    browser.fill('password', Info.PWD)
    browser.find_by_text('Log In').click()


# Log in if the browser is not yet at the login page
def complete_login():
    global browser
    browser.visit(Info.STORE_PAGE)
    simple_login()


# Method to find and return all names of the items on the current page (kept camelCase to avoid possible conflicts)
def get_item_names(get_stocks=False):
    global browser
    ### Name Parsing ###
    # Keeping the section following this one for now, but only for backup purposes
    # First, we will obtain the name of each product currently on the store
    productItemCSS = 'div.yui3-widget.sqs-widget.sqs-content-item-image.sqs-content-item-product.yui3-dd-drop div.title'
    productItemStockCSS = 'div.yui3-widget.sqs-widget.sqs-content-item-image.sqs-content-item-product.yui3-dd-drop div.stock'
    productNames = None
    product_stocks = None
    if get_stocks:
        productNames = {}
        product_stocks = csss_b(productItemStockCSS)
    else:
        productNames = []
    products = csss_b(productItemCSS)
    while len(products) == 0:
        SyS.slp(.5)
        products = csss_b(productItemCSS)
    # Obtain each product's name to use for a reference point
    for pi in range(len(products)):
        p = products[pi]
        # Try to get the name without scrolling first
        try:
            # Executing script
            runScript("return arguments[0].scrollIntoView();", p)
            WebDriverWait(browser, 3).until(EC.visibility_of_element_located(p))
            if product_stocks == None:
                productNames.append(p.text)
            else:
                productNames[p.text] = product_stocks[pi].text.split(' ')[0]
        # If that doesn't work, throw a script onto the page to scroll that name into view
        except:
            # Try executing the script without having to re-declare anything
            try:
                # Executing script
                runScript("return arguments[0].scrollIntoView();", p)
                # While any of the texts are blank, keep on re-creating the objects
                while p.text == '':
                    products2 = csss_b(productItemCSS)
                    p = products2[pi]
                # Append the found text
                if product_stocks == None:
                    productNames.append(p.text)
                else:
                    productNames[p.text] = product_stocks[pi].text.split(' ')[0]
                continue
            # If the product has gone stale, re-create the currently referenced element and go again
            except:
                # Re-creating element
                products2 = csss_b(productItemCSS)
                p2 = products2[pi]
                # Executing script
                runScript("return arguments[0].scrollIntoView();", p2)
                # While any of the texts are blank, keep on re-creating the objects
                # while p.text == '':
                #    products2 = csss_b(productItemCSS)
                #    p = products2[current]
                # Append the found text
                if product_stocks == None:
                    productNames.append(p2.text.replace('Southern Tide ', '').replace('Copy of ', ''))
                else:
                    try:
                        productNames[p2.text] = product_stocks[pi].text.split(' ')[0]
                    except:
                        products = csss_b(productItemCSS)
                        p = products[pi]
                        try:
                            productNames[p.text] = product_stocks[pi].text.split(' ')[0]
                        except:
                            try:
                                product_stocks = csss_b(productItemStockCSS)
                                productNames[p.text] = product_stocks[pi].text.split(' ')[0]
                            except:
                                products = csss_b(productItemCSS)
                                product_stocks = csss_b(productItemStockCSS)
                                p = products[pi]
                                productNames[p.text] = product_stocks[pi].text.split(' ')[0]
                # productNames.append(p.text.replace('Southern Tide ', '').replace('Copy of ', ''))
                # Increment the current value
                continue
    
    # Remove any and all empty strings obtained from the above
    if type(productNames) is list:
        for n in productNames:
            if len(re.findall('[^ ]+', n)) == 0:
                productNames.remove(n)
    
    return productNames


# Gets detailed item stocks from all relevant items
def get_item_stocks():
    # Grab the global browser
    global browser
    # Save the CSS value of the overall stocks of items first
    productItemStockCSS = 'div.yui3-widget.sqs-widget.sqs-content-item-image.sqs-content-item-product.yui3-dd-drop div.stock'
    # Save the CSS value of the names of each item
    productItemCSS = 'div.yui3-widget.sqs-widget.sqs-content-item-image.sqs-content-item-product.yui3-dd-drop div.title'
    # Create a dict to store the item's individual stocks in
    product_stocks = {}
    # Save where each product is
    products = csss_b(productItemCSS)
    # List to store the overall stocks in
    product_overall_stocks = csss_b(productItemStockCSS)
    repeats = len(products)
    # Loop through every product
    for i in range(repeats):
        # If the stock is unlimited
        if product_overall_stocks[i].text == '∞':
            # Set the overall stock to -1 to indicate such
            product_stocks[products[i].text] = -1
            # print(products[i].text)
        # Otherwise
        else:
            # Get the current name/key
            ckey = products[i].text
            # print(products[i].text)
            product_stocks[ckey] = {}
            # Open the item
            try:
                WebDriverWait(browser, 3).until(EC.visibility_of_element_located(products[i]))
                select_item(products[i])
            except:
                # Executing script
                runScript("return arguments[0].scrollIntoView();", products[i])
                # Python used Rest!
                SyS.slp(1)
                # Try to select it again
                select_item(item_name(products[i].text))
            # Get the variants tab
            variants_tab = []
            # Create a repetitions count var
            current = 0
            # While either there are still repetitions to go or the tab hasn't been found yet
            while len(variants_tab) == 0 and current < 60:
                # Try getting the tab
                try:
                    variants_tab = xpath('//div[contains(text(), "Variants")]')
                # Otherwise just forget about it
                except:
                    pass
                # Python used Rest!
                SyS.slp(.1)
                # Increment the repetitions counter
                current += 1
            # Python used Pound!
            move_and_click(variants_tab)
            # Python used Rest!
            SyS.slp(.5)
            # Grab all of the rows of variants
            rows = xpath('//div[@class="attributes"]')
            # Check to see if the complex Size fields exist
            # (checked first because if not it will give a false basic positive too)
            complex_size = len(xpath('//input[@name="Size W"]')) > 0
            # Check to see if the basic Size field exists
            basic_size = len(xpath('//input[@name="Size"]')) > 0
            # Check to see if the Color field exists
            color_exists = len(xpath('//input[@name="Color"]')) > 0
            # If there's more than one row to loop through
            if len(rows) > 1:
                # Loop through every row
                for j in range(len(rows)):
                    # If there's not a complex size, there is a basic size, and there are colors
                    if not complex_size and basic_size and color_exists:
                        # Size value
                        sv = xpath('//input[@name="Size"]')[j].value
                        # Color value
                        cv = xpath('//input[@name="Color"]')[j].value
                        # Create the key for the dict
                        key = cv + '-' + sv
                        # Get the combo's stock
                        stv = xpath('//div[@class="sqs-stock-input-content"]')[j].value
                        # Save the stock value to the given key
                        product_stocks[ckey][key] = stv
                    # If there's not a complex size, there is a basic size, and there are no colors
                    elif not complex_size and basic_size and not color_exists:
                        # Size value
                        key = xpath('//input[@name="Size"]')[j].value
                        # Grab the current rows stock input
                        stv = xpath('//div[@class="sqs-stock-input-content"]')[j].value
                        # Set the current size's stock value
                        product_stocks[ckey][key] = stv
                    # If there is a complex size and there are no colors
                    elif complex_size and not color_exists:
                        # Get the first size key
                        s1 = xpath('//input[@name="Size W"]')[j].value
                        # Get the second size key
                        s2 = xpath('//input[@name="Size L"]')[j].value
                        # Construct the final key
                        key = s1 + 'x' + s2
                        # Grab the current rows stock input
                        stv = xpath('//div[@class="sqs-stock-input-content"]')[j].value
                        # Set the current size's stock value
                        product_stocks[ckey][key] = stv
                    elif complex_size and color_exists:
                        # Get the first size key
                        s1 = xpath('//input[@name="Size W"]')[j].value
                        # Get the second size key
                        s2 = xpath('//input[@name="Size L"]')[j].value
                        # Get the Color value
                        cv = xpath('//input[@name="Color"]')[j].value
                        # Construct the final key
                        key = s1 + 'x' + s2 + '-' + cv
                        # Grab the current rows stock input
                        stv = xpath('//div[@class="sqs-stock-input-content"]')[j].value
                        # Set the current size's stock value
                        product_stocks[ckey][key] = stv
            # If there's only one thing here
            elif len(rows) == 1:
                # Just set the overall stock to the row found
                product_stocks[ckey] = xpath('//div[@class="sqs-stock-input-content"]')[0].value
            # Python used Pound!
            xpath('//a[@class="cancel"]')[0].click()
            # Python used Rest!
            SyS.slp2()
            # Check to see if the extra pop-up appeared
            if len(txt('Discard')) > 0:
                # Python used Pound!
                txt('Discard')[0].click()
                # Python used Rest!
                SyS.slp2()
        # Save where each product is
        products = csss_b(productItemCSS)
    # Return the final stocks
    return product_stocks


# endregion

# ----------------- END SHORTCUT METHODS --------------------

# ----------------- BEGIN SELECTION METHODS -----------------

# region Selection

### CSS Selector: Document Base ###
# Methods for easy execution of finding an element by CSS selector
# With these retrieval methods, a lowercase means no base (document-based), while a capital means element-based
# Document Base
# Known that only one css element will be returned
def css(css_selector):
    global browser
    return browser.find_by_css(css_selector)


# Multiple css elements will be returned
def csss(csss_selector):
    global browser
    return browser.find_by_css(csss_selector)


# Uses selenium to get the css elements
def csss_b(csss_sel):
    global browser
    return browser.driver.find_elements_by_css_selector(csss_sel)


# Finds element based on name
def name(name_selector):
    global browser
    return browser.find_by_name(name_selector)


# Finds element based on class name
def clas(clas_selector):
    global browser
    return browser.driver.find_element_by_class_name(clas_selector)


# Finds link based on part of the link text
def partLink(linkpart):
    global browser
    return browser.find_link_by_partial_text(linkpart)


# Finds element by text value
def txt(txt_in):
    global browser
    return browser.find_by_text(txt_in)


# Finds element by value property
def val(value):
    global browser
    return browser.find_by_value(value)


### CSS Selector: Element Base ###
# Specific Bases
# Known that only one css element will be returned
def Css(base, css_selector):
    try:
        return base.find_by_css(css_selector)
    except:
        try:
            return base.first.find_by_css(css_selector)
        except:
            return base.find_element_by_css_selector(css_selector)


# Multiple css elements will be returned
def Csss(base, csss_selector):
    try:
        return base.find_by_css(csss_selector)
    except:
        try:
            return base.first.find_by_css(csss_selector)
        except:
            return base.find_elements_by_css_selector(csss_selector)


# Finds element based on name
def Name(base, name_selector):
    try:
        return base.find_by_name(name_selector)
    except:
        try:
            return base.first.find_by_name(name_selector)
        except:
            return base.find_element_by_name(name_selector)


# Finds element based on class name
def Clas(base, clas_selector):
    try:
        return base.find_by_css('.' + clas_selector)
    except:
        try:
            return base.first.find_by_css('.' + clas_selector)
        except:
            return base.find_element_by_class_name(clas_selector)


### XPath Selector: Document Base ###
# Methods for easy execution of finding an element by XPATH selector
# Document base
# Returns the single result of the query
def xpath(xpath_selector):
    global browser
    return browser.find_by_xpath(xpath_selector)


# Returns all results of the query
def xpaths(xpath_selector):
    global browser
    return browser.find_by_xpath(xpath_selector)


### XPath Selector: Element Base ###
# Specific Bases
# Returns the single result of the query
def Xpath(base, xpath_selector):
    try:
        return base.find_by_xpath(xpath_selector)
    except:
        try:
            return base.first.find_by_xpath(xpath_selector)
        except:
            try:
                return base.find_element_by_xpath(xpath_selector)
            except:
                return base.find_element_by_xpath('.' + (xpath_selector))


# Returns all results of the query
def Xpaths(base, xpath_selector):
    try:
        return base.find_by_xpath(xpath_selector)
    except:
        try:
            return base.first.find_by_xpath(xpath_selector)
        except:
            return base.find_element_by_xpath('.' + (xpath_selector))


### More specific, this method finds an element based on an item name, not the element name itself ###
### In other words, the input here is plain English, not a query                                   ###
# Returns an item based on that item's name
def item_name(iname):
    return xpath('//div[contains(text(), "' + iname + '")]/../..')


# endregion

# ------------------ END SELECTION METHODS ------------------

# ----------------- BEGIN MOVEMENT METHODS ------------------

# region Movement

# Moves the cursor to the specified element
def move_to(element):
    try:
        element.mouse_over()
    except:
        try:
            element[0].mouse_over()
        except:
            pass


# Moves the cursor to the specified element and clicks it
def move_and_click(element):
    try:
        element.mouse_over()
        SyS.slp(.5)
        element.click()
    except:
        try:
            element[0].mouse_over()
            element[0].click()
        except:
            print(element, ' Failed')


# Moves the cursor to the specified element and clicks it
def move_and_double_click(element):
    try:
        element.mouse_over()
        SyS.slp(.5)
        element.double_click()
    except:
        try:
            element[0].mouse_over()
            element[0].double_click()
        except:
            pass


# Easier form of calling the above
def select_item(element):
    try:
        element.mouse_over()
        SyS.slp(.5)
        element.double_click()
    except:
        try:
            element[0].mouse_over()
            element[0].double_click()
        except:
            pass


# endregion

# ------------------ END MOVEMENT METHODS -------------------

# ------------------- BEGIN CHECK METHODS -------------------

# region Check

# Returns whether an elements is visible by checking xpath
def epx(x):
    global browser
    return browser.is_element_present_by_xpath(x)

# endregion


# -------------------- END CHECK METHODS --------------------

# ------------------- BEGIN UPDATE METHODS -------------------

# Updates chromedriver.exe in case of Browser startup failure
def update_driver():
    # Create a temporary browser using Firefox
    tb = Browser()
    # Note that this does not make use of splinter since it can't
    base_url = 'https://chromedriver.storage.googleapis.com/index.html'
    # Navigate to the url where the chromedrivers are
    tb.visit(base_url)
    # Grab all the links here
    links = tb.find_by_xpath('//tr/td/a')
    # Find the folder that goes after the last relevant one
    current_link = ''
    for i in range(len(links)):
        try:
            if links[i].html == 'icons':
                current_link = links[i-1].outer_html
                break
        except:
            pass
    # Parse the url out of this
    current_link = current_link.split('"')[1]
    tb.visit(base_url + current_link)
    # Click the driver to download it
    tb.find_by_xpath('//a[contains(text(), "win32")]')[0].click()
    # Close the browser, we're done with it
    tb.quit()
    # Import the libraries necessary for the following code
    import os, glob, zipfile, shutil
    # Save the current directory to easily get back to it
    od = os.getcwd()
    # Navigate to the Downloads folder
    os.chdir(Info.DOWNLOADS_DIR)
    # Find all of the relevant zip files located in this folder
    zips = glob.glob('chromedriver*.zip')
    # Save the first found as a default latest file and time created
    latest = zips[0]
    last_date = os.path.getctime(latest)
    # Loop through the zips and find the actual latest files
    for i in range(1, len(zips)):
        if os.path.getctime(zips[i]) > last_date:
            last_date = os.path.getctime(zips[i])
            latest = zips[i]
    # Unzip the latest downloaded driver file
    with zipfile.ZipFile(latest) as z:
        z.extractall(latest.split('.')[0])
    # Navigate into this folder
    os.chdir(latest.split('.')[0])
    # Copy this into each of the relevant folder as necessary
    for d in Info.PYTHON_DIRS:
        if os.path.getctime(d + '//chromedriver.exe') < last_date:
            try:
                shutil.copy('chromedriver.exe', d + '//chromedriver.exe')
            except:
                print('Copy failed due to admin, hopefully copying elsewhere works better...')
    os.chdir(od)

# -------------------- END UPDATE METHODS --------------------