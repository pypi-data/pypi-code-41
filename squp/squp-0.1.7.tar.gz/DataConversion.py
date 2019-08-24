'''
DataConversion.py
Version: 1.0
Author: Jonathan Hoyle
Last Updated: 11/15/2018
Description: Used to convert exported item jsons from scrapes into more usable dat formats
'''
# ---------------------- BEGIN IMPORTS ----------------------

import json, unicodedata, dataset


# ----------------------- END IMPORTS -----------------------

# ----------------------- BEGIN CLASS -----------------------

# region Base Conversion

# First Conversion class, handles turning the scraped json items into a comprehensive json database
class Conversion(object):
    
    # ---------------- BEGIN SHORTCUT METHODS -------------------
    
    # Method that does absolutely nothing, used to get rid of annoying unused prompts
    def no_op(self, anything):
        pass
    
    # ----------------- END SHORTCUT METHODS --------------------
    
    # --------------- BEGIN BASIC PARSING METHODS ---------------
    
    # Separating different values by tildes
    def tildeSeparate(self, sep):
        sepStrings = []
        st = sep.split('~')
        for s in st:
            sepStrings.append(s)
        return sepStrings
    
    # Separating different values by commas
    def commaSeparate(self, sep):
        sepStrings = []
        st = sep.split(',')
        for s in st:
            sepStrings.append(s)
        return sepStrings
    
    # ---------------- END BASIC PARSING METHODS ----------------
    
    # ---------------- BEGIN PROGRAM METHODS --------------------
    def convert(self, fileName):
        # Create the initial json object
        jd = None
        # Open and parse the json file
        with open(fileName) as data_file:
            jd = json.loads(data_file.read())
        # Create an array to hold the properly formatted json data in
        jda = {}
        # For each entry in the original data
        for j in jd:
            # Normalize the name into an ASCII string, not unicode
            try:
                # name = unicodedata.normalize('NFKD', j['name']).encode('ascii', 'ignore')
                name = j['name']
                # Set the default entry type
                dontPrint = jda.setdefault(name,
                                           {'sku': '', 'url': '', 'price': '', 'description': '', 'image_urls': [],
                                            'colors': [], 'image_paths': [], 'images': [], 'details': [], 'skus': [],
                                            'goto': [], 'origin': '', 'sizes':[], 'color_data':{}})
                # Add the information
                try:
                    # Try replacing that weird character set
                    jda[name]['description'] = j['description'].replace('&nbsp;', '').strip()
                except:
                    try:
                        # Otherwise just try to strip it
                        jda[name]['description'] = j['description'].strip()
                    except:
                        # Or just assign it
                        jda[name]['description'] = j['description']
                try:
                    # Try stripping the price var
                    jda[name]['price'] = j['price'] if (j['price'] is not str) else j['price'].strip()
                except:
                    # Otherwise just assign it
                    jda[name]['price'] = j['price']
                jda[name]['image_urls'] = j['image_urls']
                jda[name]['colors'] = j['colors']
                jda[name]['image_paths'] = j['image_paths']
                try:
                    jda[name]['color_data'] = j['color_data']
                except:
                    self.no_op(None)
                try:
                    jda[name]['origin'] = j['origin']
                except:
                    self.no_op(None)
                try:
                    jda[name]['images'] = j['images']
                except:
                    self.no_op(None)
                jda[name]['skus'] = j['skus']
                try:
                    jda[name]['goto'] = j['goto']
                except:
                    self.no_op(None)
                jda[name]['sku'] = j['sku'].strip()
                jda[name]['url'] = j['url']
                jda[name]['details'] = j['details']
                jda[name]['sizes'] = j['sizes']
            except:
                self.no_op(None)
        # Return the properly formatted json file
        return jda
    
    # ----------------- END PROGRAM METHODS ---------------------


# endregion

# ------------------------ END CLASS ------------------------

# ----------------------- BEGIN CLASS -----------------------

# region SQL Conversion

# Conversion Class that takes a file and uses its data to add/update information in the appropriate database
class SQLConversion(object):
    # Connect to the database of items
    db = dataset.connect('sqlite:///C:\\Users\\Shipping\\Documents\\Integration Dev\\SquarespaceUploader\\save_data.db')
    # Begin referencing the items table
    table = db['items']
    # Set up the basic json data variable
    jd = None
    
    # ---------------- BEGIN PROGRAM METHODS --------------------
    
    # Converts the given file
    def convert(self, file_name):
        # Open the file
        with open(file_name) as data_file:
            # And save its converted data
            jd = json.loads(data_file.read())
        # Loop through the data
        for j in jd:
            # Get all of the data from the current json item
            name = unicodedata.normalize('NFKD', j['name']).encode('ascii', 'ignore')
            # Basic assignments
            colors = j['colors']
            skus = j['skus']
            details = j['details']
            origin = j['origin']
            url = j['url']
            image_urls = j['image_urls']
            image_paths = j['image_paths']
            goto = []
            try:
                goto = j['goto']
            except:
                pass
            images = []
            try:
                images = j['images']
            except:
                pass
            while len(images) < len(colors):
                images.append('')
            while len(goto) < len(colors):
                goto.append('')
            while len(image_urls) < len(colors):
                image_urls.append('')
            while len(image_paths) < len(colors):
                image_paths.append('')
            # Price and description are a bit more complex due to strips
            description = ''
            try:
                # Try replacing that weird character set
                description = j['description'].replace('&nbsp;', '').strip()
            except:
                try:
                    # Otherwise just try to strip it
                    description = j['description'].strip()
                except:
                    # Or just assign it
                    description = j['description']
            price = ''
            try:
                # Try stripping the price var
                price = j['price'] if (j['price'] is not str) else j['price'].strip()
            except:
                # Otherwise just assign it
                price = j['price']
            # Convert the details list into a string so that it can be stored in the SQL DB
            if type(details) is list:
                details = "\n".join(details)
            if type(description) is list:
                description = " ".join(description)
            assert type(details) is not list
            # Create an extra var for the sizes that will be parsed
            sizes = []
            removes = []
            # Go through the list of colors and parse out the sizes
            for c in colors:
                try:
                    if (
                            '1' in c or '2' in c or '3' in c or '4' in c or '5' in c or '6' in c or '7' in c or '8' in c or '9' in c or '0' in c) or len(
                        c) == 1 or len(c) == 2 or (
                            len(c) == 3 and (c != 'Sky' and c != 'Red' and c != 'Fig' and c != 'Rio')) or (
                            len(c) == 4 and 'XXX' in c) or 'Fit' in c:
                        sizes.append(c)
                        removes.append(c)
                except:
                    pass
            for r in removes:
                colors.remove(r)
            # Go through each color and size
            for c in colors:
                for s in sizes:
                    # Save the current index
                    ci = colors.index(c)
                    # And update/insert the current item's information into the table
                    try:
                        self.table.upsert(dict(sku=skus[ci] + str(s), name=name, origin=origin, description=description,
                                               image_url=image_urls[ci], color=c, image=images[ci], price=price,
                                               goto=goto[ci], url=url, details=details, size=s, image_oath=image_paths[ci]),
                                          ['sku'])
                    except:
                        pass
        self.db.commit()
    # ----------------- END PROGRAM METHODS ---------------------

# endregion

# ------------------------ END CLASS ------------------------
