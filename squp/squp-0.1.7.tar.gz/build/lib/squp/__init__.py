'''
File: __init__.py
Description: Creates initial setup for the squp package
Created: 7/27/19
Version: 0.0.1
'''

# Starts the environment, import must happen within this method to prevent execution on import
def start():
    from . import InventoryGui
    InventoryGui.main()