# Contains all functions requiring User Input

import logging
from .Parsers import parseSelection
from typing import Set

def getLogLevel() -> str:
    """This functions get the log level from the user and configures the logging level
    
    Returns:
        str -- Logging Level Selected by User. It can be WARNING, DEBUG or INFO(default)
    """
    logLevel = input("Please enter the Logging Level. Options are DEBUG(For Debugging), INFO(To see what's going on)[Default] or WARNING(Only see errors or problems): ")
    if (logLevel == "WARNING"):
        logging.basicConfig(level=logging.WARNING)
    elif (logLevel == "DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    logging.info(f"User entered {logLevel} .")

    return logLevel

#get Output format from the user.
def getOutputFormat()-> str:
    """This functions takes in the output format from the user
    
    Returns:
        str -- The output format enterred by the user.
    """
    
    print("""The output format options are :
    SE -> S01E01. This is default.
    se -> s01e01
    X -> 01X01
    x -> 01x01
    0 -> 0101
    v -> season 01 episode 01
    V -> Season 01 - Episode 01""")
    
    outputFormat = input("Please enter the output format for Episode Filenames. Press [ENTER] to Go with default:")
    logging.info(f"User entered {outputFormat} .")
    return outputFormat

def getShowTitle() -> str:
    """This functions takes in show title from user
    
    Returns:
        str -- The show titles as input by the User
    """
    showTitle = input("Please enter the name of the TV Show : ")
    logging.info(f"User entered {showTitle} .")
    return showTitle

def getShowDirectory() -> str:
    """This function takes in show directory from user
    
    Returns:
        str -- The show directory as input by the User
    """
    showDirectory = input("Please enter the parent directory containing the TV Show Seasons : ")
    logging.info(f"User entered {showDirectory} .")
    return showDirectory

def userInput()-> dict:
    """The purpose of this function is to take User Input for Parameters. 
    It stores them in a dict which is passed on to function main.
    
    Returns:
        dict -- The dict contains the UserInput like log level, format, show name and show directory.
    """
    print("Welcome to Episode Fixer.")
    return {'Logging Level':getLogLevel(),'Format':getOutputFormat(),'Show Name':getShowTitle(),'Directory':getShowDirectory()}

def getParams()-> Set[str]:
    """
    This function asks the rename Parameters. 
    The user specifies the episodes which are to be renamed and which are to be skipped.
    It also confirms before asking for a rename. This ensures that we can skip a rename if we don't want it.  
    This is currently done by string formatting. In future implementations parsers may be used instead.
    
    Returns:
        Set[str] -- The set of episodes which needs to be processed.
    """

    print("""Specify the episodes.
    The format is : S01, S02E01, S01E02-05, S01-12, S01-12E11-24 / S05, S03E01, S03E02-05, S07-12, S06-12E17-24
    The episodes after '/' specify the episodes to be skipped.
    Press [ENTER] to include all episodes""")

    user_input = input("Please Input the Selection Range:")
    logging.info(f"User Enterted : {user_input}")
    logging.debug(f"Parsing the Selection Range")
    selected_episodes = parseSelection(user_input)
    logging.debug(f"Episodes in Selection Range are : {selected_episodes}")
    return selected_episodes

def getConfirmation(process:str='Process') -> bool:
    """This function gets the confirmation from the user for process.
    
    Keyword Arguments:
        process {str} -- The process which needs to be confirmed. e.g. Embedding/Renaming etc (default: {'Process'})
    
    Returns:
        bool -- If User Confirms we return True else False
    """
    confirmation = input(f"FINAL CONFIRMATION : {process} The Episodes? Press [Enter] to proceed. Any other Key to Skip : ")
    if confirmation:
        logging.info(f"{process} Aborted. User Typed {confirmation}")
        return False
    else:
        return True