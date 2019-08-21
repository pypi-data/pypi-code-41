import os
import sys

def ParsePathOS(path):
    if sys.platform == "win32":
        return path.split('\\')
    else:
        return path.split('/')

class Filesystem:
    '''Guard class containing static methods to easily check filesystem functions'''
    
    @staticmethod
    def PathExist(path):
        '''Check whether a path exists, an exception is thrown if the path doesn't exists
        
        Args:
            path (string): Path to the item
        Returns:
            (bool) Returns true on success
        '''

        # Check whether the path the file or directory exists
        if not os.path.exists(path):
            exception = f"Path - '{path}' does not exist"
            raise Exception(exception)
        return True

    @staticmethod
    def IsPath(path):
        '''Check whether a path exists
        
        Args:
            path (string): Path to the item
        Returns:
            (bool) Returns true on success or false on failure
        '''

        # Check whether the path the file or directory exists
        if not os.path.exists(path):
            return False
        return True

    @staticmethod
    def PathCwdExists(base, cwd):
        '''Check whether the current working directory is not within the base path
        
        Args:
            base (string): Base path
            cwd (string): Current working directory located within the base path
        Returns:
            (bool) Returns true on success
        '''

        basename = os.path.basename(base)
        tokenedCwd = ParsePathOS(cwd)

        if basename not in tokenedCwd:
            exception = f"Current working directory: '{cwd}' is not within in the '{base}' path"
            raise Exception(exception)
        return True    

    @staticmethod
    def IsPathCwd(base, cwd):
        '''Check whether the current working directory is not within the base path
        
        Args:
            base (string): Base path
            cwd (string): Current working directory located within the base path
        Returns:
            (bool) Returns true on success or false on failure
        '''

        basename = os.path.basename(base)
        tokenedCwd = ParsePathOS(cwd)

        if basename not in tokenedCwd:
            return False
        return True 

class Collections:
    '''Guard class containing static methods to easily check basic collection functions'''
    
    @staticmethod
    def NotNoneOrEmpty(obj):
        '''Check whether an object is none or empty, an exception is thrown when the object is not or empty
        
        Args:
            object (obj): Object which is getting checked
        Returns:
            (bool) Returns true on success
        '''

        # Check whether the object is none or empty  
        if not obj:
            exception = f"Object - '{obj}' is none or empty"
            raise Exception(exception)
        return True

class Http:
    '''Guard class containing static methods to easily check basic http functions'''

    @staticmethod
    def StatusCode(excpectedStatusCode, statusCode):
        '''Check whether the returned status codes are correct
        
        Args:
            excpectedStatusCode (StatusCode): The excpected status code
            statusCode (int): Returned status code    
        Returns:
            (bool): Returns true on success
        '''

        # Check whether the status codes are equal
        if not statusCode == excpectedStatusCode:
            raise Exception(f"Returned status code: {statusCode}, excepted status code: {excpectedStatusCode}")
        return True

class Argument:
    '''Guard class containing static methods to easily check basic argument functions'''

    @staticmethod
    def IsValid(arg):
        '''Check whether an argument is valid
        
        Args:
            arg (obj): Object which is getting checked
        Returns:
            (bool) Returns true on success or false on failure
        '''

        # Check whether the argument is valid
        if not arg:
            return False
        return True
