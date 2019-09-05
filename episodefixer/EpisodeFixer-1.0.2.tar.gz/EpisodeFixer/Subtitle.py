import logging
import os
import subprocess

# We must install mkvtools and add it to Path in order for it to work.

VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.flv'}

def getSubtitlePath(input_path: str) -> (str,str):
    """This function returns a tuple of output path name and subtitle path name
    
    Arguments:
        input_path {str} -- The path name of original video file
    
    Returns:
        (str,str) -- A tuple (subtitle path name, output file path name)
    """
    logging.debug(f"Removing the extension to extract the path name.")
    episode_name = input_path[:input_path.rfind('.')]
    subtitle_path = f"{episode_name}.srt"
    output_path = f"{episode_name}embedded.mkv"
    if os.path.isfile(subtitle_path):
        logging.info(f"Subtitle file found for {episode_name}.")
    else:
        logging.info(f"No subtitle file found for {episode_name}.")
        subtitle_path = ''
    return (subtitle_path,output_path)

def clean(input_path:str,subtitle_path:str, rm_orig=True):
    """This function removes the 
    
    Arguments:
        input_path {str} -- The path name of the original video file
        subtitle_path {str} -- The path name of the subtitle file
    
    Keyword Arguments:
        rm_orig {bool} -- argument to check if function needs to be executed. (default: {True})
    """
    if rm_orig:
        logging.info(f"Removing the video file {input_path}")
        os.remove(input_path)
        logging.info(f"Removing the subtitle file {subtitle_path}")
        os.remove(subtitle_path)
        if os.path.isfile(subtitle_path) or os.path.isfile(input_path):
            logging.error(f"Cleanup Failed. Files still exists")
        else:
            logging.info(f"Cleanup Successfull")

def executeMKVMerge(input_path:str,subtitle_path:str,output_path:str,rm_orig=False):
    """This function executes the mkvmerge script using a subprocess. It may also clean up the original files if rm_orig is True
    
    Arguments:
        input_path {str} -- The input path of the episode
        subtitle_path {str} -- The path name of the subtitle file
        output_path {str} -- The path name of the output file
    
    Keyword Arguments:
        rm_orig {bool} -- argument to check if original need to be removed. (default: {False})
    """
    logging.debug(f"Embedding Subtitles from {subtitle_path} into {input_path}")
    mkvmerge_command = ['mkvmerge','-o', output_path, input_path, subtitle_path]
    if subprocess.run(mkvmerge_command).returncode==0:
        logging.info(f"Embedding Succesfull")
        clean(input_path,subtitle_path,rm_orig)
        logging.info(f"Removing any mention of embedding.")
        os.rename(output_path,f"{output_path[-12:]}.mkv")
    else:
        logging.error(f"Embedding Failed")

def embedSubtitles(episode_path:str, rm_orig=False):
    """This function takes the path of episode and sees if there is a matching subtitle file.
    If there is subtitle file near it with same name, it will merge it and output a single mkvfile.
    
    Arguments:
        episode_path {str} -- Path name of the Episode.
    
    Keyword Arguments:
        rm_orig {bool} -- argument to check if original need to be removed. (default: {False})
    """
    if episode_path[-4:] not in VIDEO_EXTENSIONS:
        logging.warning(f"{episode_path} not a video and therefore skipped.")
    else:
        logging.info(f"Selected file {episode_path}")                
        (subtitle_path,output_path) = getSubtitlePath(episode_path)
        if subtitle_path!='':
            executeMKVMerge(episode_path,subtitle_path,output_path,rm_orig)