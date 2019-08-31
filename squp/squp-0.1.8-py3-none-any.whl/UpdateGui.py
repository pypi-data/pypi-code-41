'''
Gui Software Updater
Version 0.1
Author: Jonathan Hoyle
Created: 11/8/18
Description: Provides functionality for applying updates to the interface and corresponding libraries
'''

# Imports
from git import Repo
import os

# Main method for update procedures
def main():
    # Initialize a repo object from the current path (which is the base of the repo anyway)
    gui_repo = Repo(os.getcwd())
    # Grab the origin for the repo
    origin = gui_repo.remotes[0]
    # And pull to update the interface
    origin.pull()
    # Then check for outdated pip packages by creating the command
    check_outdated_string = 'pip list --outdated --no-cache-dir'
    # And running it and saving the results
    outdated = os.popen(check_outdated_string).read()
    # Indicate which results to not update
    dont_update = ['docker', 'spynner']
    # Save the necessary lines from the above output
    needed_updates = outdated.split('\n')[2:]
    # Create a list for the packages to update
    packs = []
    # Loop through the lines obtained
    for n in needed_updates:
        # Save the package in that line
        pack = n.split(' ')[0]
        # If it's not to be ignored
        if pack not in dont_update:
            # Append it to the list
            packs.append(pack)
    # Create the string template for updating
    update_string = 'pip install --upgrade --no-cache-dir %s'
    # Consolidate all packages that need updating to a single string
    packs_str = ' '.join(packs)
    # Execute the command created by the above two fields
    update_output = os.popen(update_string % packs_str).read()

if __name__ == '__main__':
    main()