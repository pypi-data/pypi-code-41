  
# importing logging to log and debug the code
# Importing re for Regex,
import logging
import os
import re

class Episode:
    REGEX = {
        'SE': r"S[0-9][0-9]E[0-9][0-9]", # S00E00 format , most popular and widely used,
        'se': r"s[0-9][0-9]e[0-9][0-9]", # Lowercase version of above format. 
        'S.E':r"S[0-9]+.E[0-9]+", # S0.E0 format , very rare format,
        'SE1':r"S[0-9]+E[0-9]+", # S0E0 format , very rare format,
        'x' : r"[0-9]+x[0-9][0-9]",      # 0x00 format, old school but popular and more compact,
        'X' : r"[0-9]+X[0-9][0-9]",      # lowercase version of above.
        '0' : r"[0-9][0-9][0-9][0-9]*",  # Very poor format which is basically 3 or 4 digits in which last two are for ep# and first/first two are season#
        'v' : r"season[\s]*[0-9]+[\s]*episode[\s]*[0-9]+", # Super verbose format, found knowhere but I use it so I have it.
        'V' : r"Season[\s]*[0-9]+[\s]*[-]*[\s]*Episode[\s]*[0-9]+", # Same thing as above , rare format with a " - " between data
        '2' : r"[0-9][0-9]*",            # This format is bad as we are unaware about episode data. It can be used to find ep# but season# has to inferred from folder names.
    }
    VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.srt', '.flv'}
    
    def __init__(self,show_name:str,path_name:str,show_folder:str,output_format:str):
        """Class Initializer
        We infer the ID format of the file and then, we parse the episode and season numbers.
        
        Arguments:
            show_name {str} -- The name of the TV Show
            path_name {str} -- The PATH of the episode.
            show_folder {str} -- The PATH of the TV Show directory.
            output_format {str} -- The output format for the TV Show's ID
        """
        self.show_name = show_name 
        self.season = 0
        self.episode = 0
        self.episode_title = ''
        self.extension = ''
        self.input_format = ''
        self.output_format = output_format
        break_index = path_name.rfind(os.sep) 
        self.episode_folder = path_name[:break_index]
        self.file_name = path_name[break_index+1:]
        self.show_folder = show_folder
        self.isVideo = True
        self.renameDetails = {}
        logging.debug(f"New Episode of {self.show_name} created with filename - {self.file_name}")
        self.parse()
        
    
    def ID(self, output_format:str = "SE",extension=True)-> str:
        """ Function to return ID of episodes in certain format
        
        Keyword Arguments:
            output_format {str} --  (default: {"SE"})
            extension {bool} -- To include the extension or not. (default: {True})
        
        Returns:
            str -- The ID of the episode.
        """
        season_prefix = "S"
        episode_prefix = "E"
        
        if (output_format == "x" or output_format == "X"):
            season_prefix = ""
            episode_prefix = output_format
        elif (output_format == "v"):
            season_prefix = "season "
            episode_prefix = " episode "
        elif (output_format == "V"):
            season_prefix = "Season "
            episode_prefix = " - Episode "
        elif (output_format == "0"):
            season_prefix = ""
            episode_prefix = ""
        
        # We use f-string formatting to extend Episode Number from 1 to 01. 
        season_id = f"{season_prefix}{self.season:02d}"
        episode_id = f"{episode_prefix}{self.episode:02d}"
        
        # Combining Season ID and Episode ID to get ID
        identifier = f"{season_id}{episode_id}"
        if extension:
            identifier += self.extension 
        return identifier
        
    def infer_format(self):
        """
        Function uses regex from Python's re library to find format of the filename.
        The most popular format is SE/se so we check for that first.
        Next we check for 0x00 formats which are also common
        3/4 digit letters are checked next and finally 2 digit letters are checked.
        This is because 2 letter formats might trigger on a 3 digit/4 digit formats so 
        they have to be checked last.
        
        Raises:
            ValueError: Raised in case no ID Format can be inferred.
        """
        logging.debug("Inferring ID Format.")
        for id_format in self.REGEX.keys():
            logging.debug(f"Matching episode with {id_format} .")
            match = re.search (self.REGEX[id_format], self.file_name)
            # In re.search returns a None object if it cannot find any match. 
            # However if a match is found we store the format.
            if (match != None):
                self.input_format = id_format
                logging.debug(f"Match found. Episode's format is {id_format}.")
                break

        if(id_format == ""):
            logging.exception(f"Format could not be inferred. Raising Exception")
            raise ValueError(f"No ID Format could be inferred.")
        # Logging the fact that no format is inferred.
                
    def parse(self):
        """The parse() function retrieves the file extension and episode metadata 
        (season number and episode number which is extracted as string and processed by the Decrypt ID function)     
        """
        logging.debug(f"Parsing the episode.")
        self.infer_format()
        logging.debug("Extracting Episode ID")
        extracted_id = re.search (self.REGEX[self.input_format], self.file_name).group()
        logging.debug("Extracting Episode Extension")
        self.extension = re.search(r".[a-zA-Z|0-9]+\Z",self.file_name).group()
        if self.extension not in self.VIDEO_EXTENSIONS:
            logging.error(f"{self.file_name} isn't a video or subtitle file")
            self.isVideo = False
        logging.debug("Extracting #Season and #Episode")
        self.decryptID(extracted_id)

    def decryptID(self, extracted_id:str):
        """This function extracts the episode and season info from the string supplied to it.
    
        Arguments:
            extracted_id {str} -- This is the extracted string.
        """
        
        logging.debug("Extracting Episode Number.")
        if (self.input_format == 'S.E' or self.input_format == 'SE1') :
            self.episode = int((extracted_id[extracted_id.find('E')+1:]).strip())
        else:
            self.episode = int((extracted_id[-2:]).strip()) # Extract last two letters. This is pretty common.

        logging.debug("Extracting Season Number, if available.")
        if (self.input_format == "SE" or self.input_format == "se" ):
            self.season = int((extracted_id[1:3])) # Extract two letters after S
        elif (self.input_format == "x" or self.input_format == "X" ):
            self.season = int((extracted_id[:-3])) # Extract all letters except last 3. i.e just before x
        elif (self.input_format == "0"):
            self.season = int((extracted_id[:-2])) # Extract all letters except last 3.
        elif (self.input_format == "v" or self.input_format == "V"):
            self.season = int((extracted_id[7:8]).strip()) # Get the letters after "season ". These may include a space if number is single digit so we use strip()
        elif (self.input_format == 'S.E'):
            self.season = int((extracted_id[1:extracted_id.find('.')])) # Extract letters after S and before .
        elif (self.input_format == 'SE1'):
            self.season = int((extracted_id[1:extracted_id.find('E')])) # Extract letters after S and before .
        else:
            logging.debug(f"Season not mentioned in episode with filename - {self.file_name}, infering from {self.episode_folder} .")
            self.season = int(self.episode_folder[-1])
                    
    def cleanName(self,file_name:str) -> str:
        """The function sanitizes the filename by removing all offending characters
        
        Arguments:
            file_name {str} -- The file name which needs to be cleaned in order to sanitize the characters.
        
        Returns:
            str -- The sanitized file name.
        """
        new_name = file_name.replace("*" , "").replace("?" , "").replace(":" , "").replace(">" , "").replace("<" , "").replace("/" , "").replace("\\" , "").replace("\"" , "")
        if (new_name != file_name):
            logging.debug(f"Cleaned {file_name} to {new_name} to remove special characters.")
        return new_name

    def getRenameDetails(self) -> dict:
        """This function creates the rename details of the episode. These are:
        src is the PATH of the original file which is to be renamed.
        season_folder is new folder that may need to be created in case of bad folder names.
        dst is the PATH of renamed file.
        
        Returns:
            dict -- This is dict representing the rename details of the episode.
        """
        src = f"{self.episode_folder}{os.sep}{self.file_name}"
        season_folder = f"{self.show_folder}{os.sep}Season {self.season}" #new name  
        new_name = self.cleanName(self.print())
        dst = f"{season_folder}{os.sep}{new_name}"
        
        self.renameDetails['old'] = {'Path Name' : src , 'Folder Name' : self.episode_folder , 'File Name' : self.file_name}
        self.renameDetails['new'] = {'Path Name' : dst , 'Folder Name' : season_folder , 'File Name' : new_name}
        self.renameDetails['change'] = f"{self.renameDetails['old']['File Name']} -> {self.renameDetails['new']['File Name']}"
        return self.renameDetails 

    def print(self)-> str:
        """ Print complete description of an episode. 
        We trim the show_name by removing the year using the 4 digit REGEX.
        Example if the episode is S01E01 of "The Flash 2009" called the "Pilot" and file extension is .mkv
        The output will be "The Flash S01E01 - Pilot .mkv"
        
        Returns:
            str -- The new file name of the episode with Show Name, Episode ID and Episode Title.
        """
        trimmed_show_name = self.show_name
        match = re.search (r"[0-9][0-9][0-9][0-9]", self.show_name)
        if (match != None):
            trimmed_show_name = trimmed_show_name.replace(match.group(),"").strip()                
        return f"{trimmed_show_name} {self.ID(self.output_format,extension=False)} - {self.episode_title} {self.extension}"

    # This is same as print.
    def __str__(self)-> str:
        """This is same as print
        
        Returns:
            str -- print title of the file.
        """
        return print(self)