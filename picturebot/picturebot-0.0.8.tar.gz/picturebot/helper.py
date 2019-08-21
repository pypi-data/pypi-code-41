import os
from dataclasses import dataclass
import generalutils.guard as grd

@dataclass
class Config:
    '''POCO class for config data'''

    Workplace: str = ""
    Workflow: str = ""
    Baseflow: str = ""
    Backup: str = ""
    Selection: str = ""
    Edited: str = ""

def FullFilePath(*items):
    '''Get the full path to a folder or directory
    Args:
        items (list): List of folders and subfolders
    
    Returns:
        (string) Full file name
    '''

    # Get the current working directory
    path = os.path.dirname(os.path.abspath(__file__))

    # Loop over every folder and subfolders
    for item in items:
        path = os.path.join(path, item)

    return path

def CreateFolder(path):
    '''Create And test whether the folder is successfully created
    
    Args:
        path (string): Folder that is going to get created
    '''

    if not grd.Filesystem.IsPath(path):
        # Create folder
        os.mkdir(path)

        # Check whether creation was successfull
        grd.Filesystem.PathExist(path)
