# File contains Functions to rename episodes
import logging
import os
from datetime import datetime
from .UserInput import getParams,getConfirmation

def previewRename(episodes:dict):
    """This function gives a preview of the name change of the episodes.
    
    Arguments:
        episodes {dict} -- Dictionary containing the rename details of the episodes.
    """
    for episode_id in episodes.keys():
        episode_info = episodes[episode_id]
        logging.warning(episode_info['change'])

def getRenameEpisodes(episodes:dict) -> dict:
    """This function gets the rename_episodes dict from the user selection set. It calls getParams()
    
    Arguments:
        episodes {dict} -- Dictionary containing the rename details of the episodes
    
    Returns:
        dict -- Dictionary which is contains selected episodes that are to be renamed.
    """
    user_selection_set = getParams()
    #This takes an intersection of existing episodes and the user selection range to give us the episodes that can be renamed.
    rename_episodes = {episodeID:episodes[episodeID] for episodeID in episodes if episodeID[:6] in user_selection_set}
    logging.info(f"User selected the following episodes {rename_episodes.keys()}") 
    return rename_episodes

def executeRename(rename_episodes:dict,folder_name:str):
    """This function actually executes the rename of the episodes. 
    It also logs the changes in a history file.
    
    Arguments:
        rename_episodes {dict} -- Dictionary which is contains selected episodes that are to be renamed.
        folder_name {str} -- Path Name of the Directory containing all the episodes.
    """
    # Creating History File to store rename History.
    history_file = open(f'{folder_name}{os.sep}Rename History {datetime.now().strftime("%Y-%m-%d %H.%M")}.log', "w+",encoding='utf-8')
    #Renaming Episodes.
    logging.debug(f"Executing Rename.")
    for episode_id in rename_episodes:
        episode_info = rename_episodes[episode_id]    
        logging.warning(episode_info['change'])
        season_folder = episode_info['new']['Folder Name']
        try:
            if not os.path.exists(season_folder):
                os.makedirs(season_folder)
                logging.debug(f"New Folder created: {season_folder}")
            if os.path.exists(season_folder):
                os.rename(episode_info['old']['Path Name'],episode_info['new']['Path Name'])
                logging.info(f"Rename Executed: Episode is now {episode_info['new']['File Name']}")
                history_file.write(f"{episode_info['change']}\n")
        except Exception as e:
            logging.exception(f"Rename Failed : Raised {repr(e)}. Episode is still {episode_info['old']['File Name']} ")
            history_file.write(f" Rename Failed for {episode_info['old']['Path Name']} due to {repr(e)} \n")
    history_file.close()                    

def renameShow(episodes:dict,folder_name:str):
    """Master Function which renames the Show's episodes.
    
    Arguments:
        episodes {dict} -- Dictionary containing the rename details of the episodes.
        folder_name {str} -- Path Name of the Directory containing all the episodes.
    """
    
    logging.info(f"Previewing New File Names for All Episodes.") 
    previewRename(episodes)
    rename_episodes = getRenameEpisodes(episodes)
    logging.info(f"Previewing New File Names for Selected Episodes.") 
    previewRename(rename_episodes)
    if getConfirmation(process='Rename') :
        executeRename(rename_episodes,folder_name)