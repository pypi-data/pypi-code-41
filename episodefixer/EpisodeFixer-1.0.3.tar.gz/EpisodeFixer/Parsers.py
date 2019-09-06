# Function which involve parsing user input
import logging
import re

#REGEX_SS is a global variable and hence all functions have access to it.
REGEX_SS = {
    'S-E-': r"S[0-9][0-9]-[0-9][0-9]E[0-9][0-9]-[0-9][0-9]" , # SXX-YYEXX-YY Range in both Episode and Season
    'SE-' : r"S[0-9][0-9]E[0-9][0-9]-[0-9][0-9]"            , # SXXEXX-YY Season Fixed and Range in Episode
    'S-E' : r"S[0-9][0-9]-[0-9][0-9]E[0-9][0-9]"            , # SXX-YYEYY Episode Fixed and Range in Season
    'S-'  : r"S[0-9][0-9]-[0-9][0-9]"                       , # SXX-YY Range in Season
    'SE'  : r"S[0-9][0-9]E[0-9][0-9]"                       , # SXXEYY Fixed Season Fixed Episode
    'S'   : r"S[0-9][0-9]"                                  , # SXX Fixed Season All Episodes
}

def createRange(subselection:str, excluded=True)-> List[str]:
    """This function converts subselections with a given format into an episode list.
    
    Arguments:
        subselection {str} -- This represents the range of episodes under consideration
    
    Keyword Arguments:
        excluded {bool} -- If True, the episodes will be excluded else they will be included (default: {True})
    
    Returns:
        List[str] -- A List containing all episodes in the range
    """
    # Default values for min and max are 0 and 99. 
    # These are the minimum and maximum digits that can be represented in 2 digits.
    season_min = 0
    season_max = 99
    episode_min = 0
    episode_max = 99
    
    if subselection == '' and excluded :
        return []
    subselection_format = infer_format(subselection)
    
    if (subselection_format.startswith("S-")):
        season_min = int(subselection[1:3])
        season_max = int(subselection[4:6])
    elif (subselection_format.startswith("S")):
        season_min = int(subselection[1:3])
        season_max = season_min
    
    if (subselection_format.endswith("E-")):
        episode_min = int(subselection[-5:-3])
        episode_max = int(subselection[-2:])
    elif (subselection_format.endswith("E")):
        episode_min = int(subselection[-2:])
        season_max = season_min
    
    logging.debug(f"The theoretical range for {subselection} is S{season_min:02d}-{season_max:02d}E{episode_min:02d}-{episode_max:02d}")
    #We want to include both endpoints.
    episodeRange = [f"S{season:02d}E{episode:02d}" for episode in range(episode_min,episode_max+1) for season in range(season_min,season_max+1)]
    logging.debug(f"The episodes in the subselection {subselection} were {episodeRange}")    
    return episodeRange

def infer_format(subselection:str) -> str:
    """
    Function to Infer the Format of User Selection Input and return the REGEX_SS Key to it.
    This function uses regex from Python's re library to find format of the query.
    They are checked in the order of insertion. 
    This is to make sure range selections don't get mixed with singleton selection.
    
    Arguments:
        subselection {str} -- This represents the episode range whose format we need to infer.

    Raises:
        ValueError: Exception is raised if no Subselection ID can be inferred.
    
    Returns:
        str -- Key of the Subselection Format inferred from the Subselection
    """
    for subselection_format in REGEX_SS.keys(): #iterating over REGEX_SS's keys.
        logging.debug(f"Matching {subselection} with {subselection_format} .")
        match = re.search (REGEX_SS[subselection_format], subselection)
        # In re.search returns a None object if it cannot find any match. 
        # However if a match is found we return.
        if (match != None):
            logging.debug(f"Match found. Subselection format is {subselection_format}.")
            return subselection_format
        
    if(subselection_format == "" and subselection != ""):
        logging.exception(f"Illegel Selection from User, Format could not be inferred. Raising Exception")
        raise ValueError(f"Subselection ID Format could be inferred.")
        # Logging the fact that no format is inferred.
    logging.warning(f"Returning Empty String for subselection: {subselection}")
    return "" #Returning an Empty String in case of no format being found.

def processConsiderations(considered_part:str, selected=True) -> List[str]:
    """This function takes in considered_part and returns the range corresponding to it.
    
    Arguments:
        considered_part {str} -- This represents the episodes we are considering for either selection or exclusion.
    
    Keyword Arguments:
        selected {bool} -- Boolean representing the nature of consideration. (default: {True})
    
    Returns:
        List[str] -- all the episodes specified in the considered_part.
    """
    Considered = {True:'Selected', False:'Excluded'}[selected]
    considerationRange = []
    
    logging.info(f"The {Considered} Part is {considered_part}")
    subconsiderations = considered_part.replace(' ','').split(',')
    
    for subconsideration in subconsiderations:
        logging.debug(f"Started processing {subconsideration}.")
        subconsideration_range = createRange(subconsideration, excluded=not selected)
        considerationRange += subconsideration_range #Concat Consideration Lists
        logging.debug(f"Added {subconsideration_range} to {Considered} Files.")
    return considerationRange

def parseSelection(selection:str)-> set[str]:
    """This is the parser function for the selection.
    
    Arguments:
        selection {str} -- String containing both the episodes which are selected and excluded.
    
    Returns:
        set[str] -- A set of all episodes which were specified by the selection string.
    """
    selected_part = ""
    excluded_part = ""
    pos_seperator = selection.find('/')
    if(pos_seperator != -1):
        logging.debug("Seperator Found. Range into Selected and Excluded Part")
        selected_part = selection[:pos_seperator]
        excluded_part = selection[pos_seperator+1:]
    else:
        selected_part = selection

    selected_files = processConsiderations(selected_part,selected=True)
    excluded_files = processConsiderations(excluded_part,selected=False)
    
    #This converts sorted and excluded lists into sets and computes their difference set.               
    logging.debug(f"Removing Excluded files from Selected Files.")
    return set(selected_files)-set(excluded_files) 