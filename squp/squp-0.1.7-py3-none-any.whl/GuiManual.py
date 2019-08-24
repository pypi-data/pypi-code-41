'''
Gui Manual
Version 0.2
Author: Jonathan Hoyle
Created: 11/1/18
Description: Provides a graphical manual for the interface for the online store
Details: Can be run from the interface or by itself using flexx tech
'''

# Imports
import webview, dominate
from information import Info
from dominate.tags import *
from bottle import route, run, template

# Tricking something for some reason
window = None

# Style import
g_CSS = open('base_bootstrap.css').read()

# Associate the assets appropriately (materia, minty works)
url = 'https://stackpath.bootstrapcdn.com/bootswatch/4.1.2/yeti/bootstrap.min.css'

# Set up dominate documents
home = dominate.document()

# Set up the styling and jquery
with home.head:
    link(rel='stylesheet', href=url)
    script(src='https://code.jquery.com/jquery-2.1.1.min.js')
    
# Create the home page
with home:
    with div(cls='container', id='home'):
        # Page title
        with h1(id='home'):
            span('Lionel Smith Ltd Custom Interface')
        # Welcome section
        with div(cls='row'):
            p('Welcome to the Lionel Smith Ltd. Custom Interface help page! '
              'Please choose a section below to navigate to the proper page\'s help section.')
        # Links section
        with div(cls='row'):
            a('Orders', href='#orders', cls='btn btn-primary col-sm-2')
            a('Item Database', href='#database', cls='btn btn-primary col-sm-2')
            a('Updates', href='#updates', cls='btn btn-primary col-sm-2')
            a('Manage Inventory', href='#manage', cls='btn btn-primary col-sm-2')
            a('Create/Edit Item', href='#create_edit', cls='btn btn-primary col-sm-2')
            a('FAQ', href='#faq', cls='btn btn-primary col-sm-2')
        p()
        
        # Order title
        with h1(id='orders'):
            span('Orders Page')
        # Reference image
        with div(cls='row'):
            img(src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/OrdersPage.png')
        # Overview
        with h3():
            span('Overview')
        with div(cls='row'):
            p('This page provides an interface to see and fulfill orders from the online store. Note that this page '
              'has a sort of online equivalent, but this should prove to be faster and more intuitive.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span('Dropdown list of all orders currently listed online, note that it does not update live, so '
                        'any time updates are needed the program will need to be restarted.'))
                li(span('Shipping tracking information goes here, checks to make sure the tracking number entered is '
                        'valid and if it\'s not will ask for correction and will not allow saving.'))
                li(span('Completes the order in this interface, but does not proceed with fulfilling the order, just '
                        'marks it as ready.'))
                li(span('Saves currently completed orders but does not execute them, just saves the data entered if '
                        'it\'s valid.'))
                li(span('This actually executes the completion of these orders, note that this is where the remote '
                        'agent comes in on this page and it may take a while.'))
                li(span('This will restart the program to update the orders currently online, note that it will ask '
                        'for permission before doing so.'))
                li(span('This button opens the original orders page in Google Chrome.'))
                li(span('Customer name appears here.'))
                li(span('Customer shipping information appears here.'))
                li(span('Corresponding item information appears here, note that each item will be displayed.'))
        with div(cls='row'):
            a('Return to top', href='#home', cls='btn btn-primary')
                
        # Database Page
        with h1(id='database'):
            span('Database Page')
        # Reference image
        with div(cls='row'):
            img(src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/Database.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p('This page allows browsing of all items that are currently being tracked, whether on the store or not.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span('Tree view of all items in the database, click + button to expand items and double click the '
                        'item to populate the fields on the left.'))
                li(span('Checkboxes for each field, if you don\'t want a particular field to every change, select it '
                        'here and updates will not be applied to that field until the field is unchecked again.'))
                li(span('Item details go in these blanks, one line for the first few and multiple lines for the '
                        'bottom fields.'))
                li(span('If possible, an image of the selected item is shown here for reference, defaults to the image '
                        'shown.'))
                li(span('As the inner text implies, clicking this button will navigate you to the create/edit page of '
                        'this interface with the current item selected.'))
                
        # Database Page
        with h1(id='updates'):
            span('Updates Page')
        # Reference image
        with div(cls='row'):
            img(src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/Updates.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p(
                'This page shows the items that have changed between their last edit and the current data, and '
                'shows what will be changed')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span(
                    'Tree view of all items that have changes, double clicking an item will populate the right side.'))
                li(span(
                    'Clicking this completely disables the update for this item, swaps to say "Enable Update" when '
                    'the item is disabled.'))
                li(span(
                    'Clicking this refreshes the updates needed, note that due to background processes this may take a '
                    'while and probably will not apply until the program is restarted.'))
                li(span(
                    'Takes all of the currently enabled updates and applies them to the online store.'))
                li(span(
                    'This column shows the item\'s current information on the store.'))
                li(span(
                    'This column shows the item\'s new information from the most recent scrape.'))
        with div(cls='row'):
            a('Return to top', href='#home', cls='btn btn-primary')
                
        # Inventory Management Page
        with h1(id='manage'):
            span('Inventory Management Pages')
        
        # Show/Hide Items Page
        with h2(id='show_hide'):
            span('Show/Hide Items Page')
        # Reference image
        with div(cls='row'):
            img(src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/InventoryManageShow.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p(
                'This page shows the items currently uploaded to the store, whether shown or not, and allows showing '
                'and hiding those items.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span(
                    'Lists of every item currently uploaded and not shown sorted by origin store. Currently, only one '
                    'item from each list is selectable at a time, multiple selection coming in a future update.'))
                li(span(
                    'Clicking this button moves the item(s) selected on the left side and moves them to the right. '
                    'Note that this is only a graphic representation of a possible change, doing this does NOT '
                    'actually show the item(s) in the store.'))
                li(span(
                    'Clicking this button moves the item(s) selected on the right side and moves them to the left. '
                    'Note that this is only a graphic representation of a possible change, doing this does NOT '
                    'actually hide the item(s) in the store.'))
                li(span(
                    'Pressing this button will take the changes made in this interface and apply them to the actual '
                    'store. Note that this may take a little while.'))
                li(span(
                    'Currently shown items on the store. Selection rules are currently the same as the left side.'))
                li(span(
                    'Sub-tab for uploading items not currently on the store.'))
                li(span(
                    'Sub-tab for managing item stocks.'))
        with div(cls='row'):
            a('Return to section top', href='#manage', cls='btn btn-primary')
            a('Return to top', href='#home', cls='btn btn-primary')
            
        # Upload Items page
        with h2(id='upload'):
            span('Upload Items Page')
        # Reference image
        with div(cls='row'):
            img(src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/InventoryManageUpload.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p(
                'This page shows all items tracked, whether uploaded to the store or not, and allows for local items '
                'to be uploaded to the online store.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span(
                    'Lists of every item currently not uploaded to the store. Selection rules are one item from each '
                    'list, expanded selection coming in future update.'))
                li(span(
                    'Clicking this button moves the item(s) selected on the left side and moves them to the right. '
                    'Note that this is only a graphic representation of a possible change, doing this does NOT '
                    'actually upload the item(s) to the store.'))
                li(span(
                    'Pressing this button will take the changes made in this interface and mark them for completion '
                    'during the next update. In other words, this tells the interface to accomplish these actions '
                    'THE NEXT TIME THE ITEMS ARE UPDATED, not at the time of the button press.'))
                li(span(
                    'Currently uploaded items on the store. Selection rules are irrelevant here as this only covers '
                    'uploading, not deletion.'))
        with div(cls='row'):
            a('Return to section top', href='#manage', cls='btn btn-primary')
            a('Return to top', href='#home', cls='btn btn-primary')
        
        # Stock Management Page
        with h2(id='stock'):
            span('Stock Management Page')
        # Reference image
        with div(cls='row'):
            img(cls='col-sm-6',
                src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/InventoryManageStockTop.png')
            img(cls='col-sm-6',
                src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/InventoryManageStockOpened.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p(
                'This page shows all online items and allows for their stocks to be managed.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span(
                    'Main panel for each item.'))
                li(span(
                    'Clicking this button expands/contracts the attached panel to show/hide the stocks for that item.'))
                li(span(
                    '(a.) Decrements the current stock for the given item/size combo. \n'
                    '(b.) Current number of items in stock. The amount -1 indicates unlimited stock. \n'
                    '(c.) Increments the current stock for the given item/size combo, makes unlimited stock convert '
                    'to limited if the current stock is -1, requires reload to take effect though.'))
                li(span(
                    'Applies current changes to store immediately and will take some time. Make sure '
                    'to update items before and after this is run to ensure total store accuracy.'))
                li(span('Example of item/size combos in action with limited stocks.'))
                li(span('An item/size combination with no stock.'))
                li(span('An item/size combination with one in stock.'))
        with div(cls='row'):
            a('Return to section top', href='#manage', cls='btn btn-primary')
            a('Return to top', href='#home', cls='btn btn-primary')
        
        # Database Page
        with h1(id='create_edit'):
            span('Create/Edit Items Page')
        # Reference image
        with div(cls='row'):
            img(cls='col-sm-6', src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/CreateEditUnsized.png')
            img(cls='col-sm-6', src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/CreateEditSizedScrolled.png')
        with div(cls='row'):
            img(cls='col-sm-12', src='file:///C:/Users/Shipping/Documents/Integration%20Dev/SquarespaceUploader/imgs/CreateEditSized.png')
        # Overview section
        with h3():
            span('Overview')
        with div(cls='row'):
            p('This page allows the editing of items in the database, as well as the creation of original items.')
        # Explanations section
        with h3():
            span('Contents')
        with div(cls='row'):
            with ol():
                li(span('Initial view of this page, due to platform restrictions I cannot change this, resizing allows '
                        'the second option.'))
                li(span('Item tree which functions similarly to the others, expand tree and double click an item to '
                        'populate relevant fields on the right side of the page.'))
                li(span('Item fields for item data entry.'))
                li(span('Note that for images, a file entry field is used, which will pop up an extra window to allow '
                        'selection of one or more image files for an item.'))
                li(span('This button clears the fields on the left side to allow for new item creation.'))
                li(span('This button saves the changed information for pre-existing items or adds a new item to the '
                        'overall database depending on what has been accomplished here.'))
                li(span('The selection of these fields changes entry to allow/show more complex size options, the '
                        'initial selection being for basic sizes (i.e. S, M, L, XL, etc.) and the alternate being for '
                        'more complex sizes (i.e. pant sizes, multi-field shoe sizes, etc.)'))
        with div(cls='row'):
            a('Return to top', href='#home', cls='btn btn-primary')
                
        # FAQ Page
        with h1(id='faq'):
            span('Frequently Asked Questions')
        # Questions
        with div(cls='container'):
            with h3():
                span('I made changes in the interface, but nothing happened on the store.')
            p('Depending on what you changed, there may not need to be changes to the store, or maybe the changes '
              'weren\'t saved. Make sure that after you are done making changes you hit the corresponding save/apply '
              'button. Remember that for convenience and security, all changes made are not uploaded until approved '
              'either in this interface or on the store itself.')
            with h3():
                span('I can\'t select multiple items in the Show/Hide page and/or Upload page.')
            p('This issue is known and will be implemented in future releases, but because of the way the code '
              'behind it works, this is not yet possible. For now, just choose one item at a time from each brand, as '
              'you can use multiple brands at once, just not multiple items from the same brand at once.')
        with div(cls='row'):
            a('Return to top', href='#home', cls='btn btn-primary')
        
            
@route('/')
def root():
    return template(str(home))

def main():
    import threading
    thread = threading.Thread(target=run, kwargs=dict(host='localhost', port=8081), daemon=True)
    thread.start()
    import time
    time.sleep(1)
    webview.create_window('Interface Manual', 'http://localhost:8081', width=1000, height=600)

if __name__ == '__main__':
    main()