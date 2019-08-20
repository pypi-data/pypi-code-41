# -*- encoding: utf-8 -*-

#  Copyright 2019-  DNB
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time
import os
import socket
import re
from rbfZOS.py3270 import Emulator
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import Matcher


class x3270(object):
    def __init__(self, visible=True, timeout='30', wait_time='0.5', wait_time_after_write='0', img_folder='.'):
        """You can change to hide the emulator screen set the argument visible=${False}
           
           For change the wait_time see `Change Wait Time`, to change the img_folder
           see the `Set Screenshot Folder` and to change the timeout see the `Change Timeout` keyword.
        """
        self.lu = None
        self.host = None
        self.port = None
        self.credential = None
        self.imgfolder = img_folder
        # Try Catch to run in Pycharm, and make a documentation in libdoc with no error
        try:
            self.output_folder = BuiltIn().get_variable_value('${OUTPUT DIR}')
        except Exception as e:
            if hasattr(e, 'message') and e.message == 'Cannot access execution context': self.output_folder = os.getcwd()
#            else: raise AssertionError(e)
        self.wait = float(wait_time)
        self.wait_write = float(wait_time_after_write)
        self.timeout = int(timeout)
        self.mf = Emulator(visible=bool(visible), timeout=int(timeout))

    @keyword(name=None, tags=("Settings",))
    def change_timeout(self, seconds):
        """*Change the timeout for connection in seconds.*
        """
        self.timeout = float(seconds)

    @keyword(name=None, tags=("Settings",))
    def open_connection(self, host, LU=None, port=23):
        """*Create a connection with IBM3270 mainframe with the default port 23.*         
        
        *Arguments*
        
        ``host``: Provide the hostname as IP address to make a connection with mainframe
        
        ``LU``: Optional. Provide the Logical Unit Name
        
        ``port``: Optional. Default port is 23.
        
        
        *Examples*
        
            | `Open Connection` | 10.3.51.71 |
            | `Open Connection` | 10.3.51.71 | LU=LUname |
            | `Open Connection` | 10.3.51.71 | port=992 |
        """
        self.host = host
        self.lu = LU
        self.port = port
        if self.lu:
            self.credential = "%s@%s:%s" % (self.lu, self.host, self.port)
        else:
            self.credential = self.host
        self.mf.connect(self.credential)

    @keyword(name=None, tags=("Settings",))
    def close_connection(self):
        """*Disconnect from the host.*
        """
        try:
            self.mf.terminate()
        except socket.error:
            pass

    @keyword(name=None, tags=("Settings",))
    def change_wait_time(self, wait_time):
        """*To give time for the mainframe screen to be "drawn" and receive the next commands.* 
        To change the default value of 0.5, use this keyword passing the time in seconds.
        
        *Arguments*
        
        ``wait_time``: Provide the wait time so that a sleep applies after the following keywords `Execute Command`, `Send Enter`, `Send PF`, `Write`, `Write in position`
        
        *Examples*
        
            | `Change Wait Time` | 0.5 |
            | `Change Wait Time` | 2 |
        """
        self.wait = float(wait_time)

    @keyword(name=None, tags=("Settings",))
    def change_wait_time_after_write(self, wait_time_after_write):
        """*To give the user time to see what is happening inside the mainframe.*
        To change the default value of 0 seconds, use this keyword passing the time in seconds. 
        Note: This keyword is useful for debug purpose
        
        *Arguments*
        
        ``wait_time_after_write``: Provide the wait time so that a sleep applies after the string is sent in the following keywords `Write`, `Write Bare`, `Write in position`, `Write Bare in position`       

        Examples:
            | Change Wait Time After Write | 0.5 |
            | Change Wait Time After Write | 2 |
        """
        self.wait_write = float(wait_time_after_write)

    @keyword(name=None, tags=("Settings",))
    def read(self, ypos, xpos, length):
        """*Read a string of "length" at screen co-ordinates "ypos"/"xpos".*
           
           
           *Arguments*
           
           ``ypos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal. 
           
           ``xpos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal.
           
           ``length``: Numeric Unit. Length of the string
           
           
           *Examples*
           
               | ${value} | Read | 8 | 10 | 15 | #Read a string in the position y=8 / x=10 of a length 15 |
        """
        self._check_limits(ypos, xpos)
        # Checks if the user has passed a length that will be larger than the x limit of the screen.
        if int(xpos) + int(length) > (80+1):
            raise Exception('You have exceeded the x-axis limit of the mainframe screen')
        string = self.mf.string_get(int(ypos), int(xpos), int(length))
        return str(string)

    @keyword(name=None, tags=("Settings",))
    def execute_command(self, cmd):
        """Execute x3270 command.*
           
           *Arguments*
           
           ``cmd``: [http://x3270.bgp.nu/wc3270-man.html#Actions|x3270 command] 
           
           
           *Examples*
           
               | `Execute Command` | Enter |
               | `Execute Command` | Home |
               | `Execute Command` | Tab |
               | `Execute Command` | PF(1) |
        """
        self.mf.exec_command((str(cmd)).encode("utf-8"))
        time.sleep(self.wait)

    @keyword(name=None, tags=("Settings",))
    def set_screenshot_folder(self, path):
        """*Set a folder to keep the html files generated by the `Take Screenshot` keyword.*
           
           *Arguments*
           
           ``path``: location of folder with absolute path 
           
           *Examples*
           
               | Set Screenshot Folder | /path/to/folder |
        """
        if os.path.exists(os.path.normpath(os.path.join(self.output_folder, path))):
            self.imgfolder = path
        else:
            logger.error('Given screenshots path "%s" does not exist' % path)
            logger.warn('Screenshots will be saved in "%s"' % self.imgfolder)

    @keyword(name=None, tags=("Settings",))
    def take_screenshot(self, height='410', width='670'):
        """*Generate a screenshot of the IBM 3270 Mainframe in a html format.* 
        The default folder is the log folder of RobotFramework, if you want change see the `Set Screenshot Folder`.

           The Screenshot is printed in a iframe log, with the values of height=410 and width=670, you
           can change this values passing them from the keyword. 

           *Arguments*
           
           ``height``: Default is 410.
           
           ``width``: Default is 670.   
           
           *Examples*
           
               | `Take Screenshot` |
               | `Take Screenshot` | height=500 | width=700 |
        """
        filename_prefix = 'screenshot'
        extension = 'html'
        filename_sufix = str(int(round(time.time() * 1000)))
        filepath = os.path.join(self.imgfolder, '%s_%s.%s' % (filename_prefix, filename_sufix, extension))
        self.mf.save_screen(os.path.join(self.output_folder, filepath))
        logger.write('<iframe src="%s" height="%s" width="%s"></iframe>' % (filepath.replace("\\", "/"), height, width),
                     level='INFO', html=True)

    @keyword(name=None, tags=("Settings",))
    def wait_field_detected(self):
        """*Wait until the screen is ready, the cursor has been positioned on a modifiable field, and the keyboard is unlocked.*
        Sometimes the server will "unlock" the keyboard but the screen
        will not yet be ready.  In that case, an attempt to read or write to the
        screen will result in a 'E' keyboard status because we tried to read from
        a screen that is not yet ready.
        Using this method tells the client to wait until a field is
        detected and the cursor has been positioned on it.
        """
        self.mf.wait_for_field()

    @keyword(name=None, tags=("Settings",))
    def delete_char(self, ypos=None, xpos=None):
        """*Delete character under cursor. To delete character in another position, pass the co-ordinates "ypos"/"xpos".*
                     
           
           *Arguments*
           
           ``ypos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal. 
           
           ``xpos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal.   
           
           *Examples*
           
               | `Delete Char` |
               | `Delete Char` | ypos=9 | xpos=25 |
        """
        if ypos is not None and xpos is not None:
            self.mf.move_to(int(ypos), int(xpos))
        self.mf.exec_command(b'Delete')

    @keyword(name=None, tags=("Settings",))
    def delete_field(self, ypos=None, xpos=None):
        """Delete contents in field at current cursor location and positions cursor at beginning of field. To delete a field in another position,  pass the coordinates "ypos"/"xpos".* of any part of the field.
                      
           *Arguments*
           
           ``ypos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal. 
           
           ``xpos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal.   
           
           
           *Examples*
           
               | `Delete Field` |
               | `Delete Field` | ypos=12 | xpos=6 |
        """
        if ypos is not None and xpos is not None:
            self.mf.move_to(int(ypos), int(xpos))
        self.mf.exec_command(b'DeleteField')

    @keyword(name=None, tags=("Settings",))
    def send_enter(self):
        """Send Enter to the screen.*
        """
        self.mf.send_enter()
        time.sleep(self.wait)

    @keyword(name=None, tags=("Settings",))
    def move_next_field(self):
        """*Move cursor to the next input field. Equivalent to pressing the Tab key.*
        """
        self.mf.exec_command(b'Tab')

    @keyword(name=None, tags=("Settings",))
    def move_previous_field(self):
        """*Move the cursor to the previous input field. Equivalent to pressing the Shift+Tab keys.*
        """
        self.mf.exec_command(b'BackTab')

    @keyword(name=None, tags=("Settings",))
    def send_PF(self, PF):
        """*Send a Program Function to the screen.*
        
        *Examples*
        
               | `Send PF` | 3 |
        """
        self.mf.exec_command(('PF('+str(PF)+')').encode("utf-8"))
        time.sleep(self.wait)

    @keyword(name=None, tags=("Settings",))
    def write(self, txt):
        """*Send a string to the screen at the current cursor location. Enter is executed by default with this keyword.*
           
           *Arguments*
           
           ``txt``: String to be passed 
           
           
           *Examples*
           
               | `Write` | something |
        """
        self._write(txt, enter='1')

    @keyword(name=None, tags=("Settings",))
    def write_bare(self, txt):
        """*Send only the string to the screen at the current cursor location.*
           
           *Arguments*
           
           ``txt``: String to be passed 
           
           *Examples*
           
               | `Write Bare` | something |
        """
        self._write(txt)

    @keyword(name=None, tags=("Settings",))
    def write_in_position(self, txt, ypos, xpos):
        """*Send a string to the screen at screen co-ordinates "ypos"/"xpos". Enter is executed by default with this keyword.*
                      
           *Arguments*
           
           ``txt``: String to be passed 
           
           ``ypos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal. 
           
           ``xpos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal.  
           
           *Examples*
           
               | `Write in Position` | something | 9 | 11 |
        """
        self._write(txt, ypos=ypos, xpos=xpos, enter='1')

    @keyword(name=None, tags=("Settings",))
    def write_bare_in_position(self, txt, ypos, xpos):
        """*Send only the string to the screen at screen co-ordinates "ypos"/"xpos".*
           
           *Arguments*
           
           ``txt``: String to be passed 
           
           ``ypos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal. 
           
           ``xpos``: Numeric Unit. Co-ordinate is 1 based, listed in the status area of the terminal.  
           
           
           *Examples*
           
               | `Write Bare in Position` | something | 9 | 11 |
        """
        self._write(txt, ypos=ypos, xpos=xpos)

    def _write(self, txt, ypos=None, xpos=None, enter='0'):
        txt = txt.encode('utf-8')
        if ypos is not None and xpos is not None:
            self._check_limits(int(ypos), int(xpos))
            self.mf.move_to(int(ypos), int(xpos))
        if not isinstance(txt, (list, tuple)): txt = [txt]
        [self.mf.send_string(el) for el in txt if el != '']
        time.sleep(self.wait_write)
        for i in range(int(enter)):
            self.mf.send_enter()
            time.sleep(self.wait)

    @keyword(name=None, tags=("Settings",))
    def wait_until_string(self, txt, timeout=5):
        """*Wait until a string exists on the mainframe screen to perform the next step.* 
        If the string not appear on 5 seconds (default timeout) the keyword will raise a exception. Default timeout can be overridden by passing desired value to ``timeout``
           
           
           *Arguments*
           
           ``txt``: String to be passed 
           
           ``timeout``: Default is 5 seconds. Can be overridden by passing timeout in seconds.
           
           
           *Examples*
           
               | `Wait Until String` | something |
               | `Wait Until String` | something | timeout=10 |
        """
        max_time = time.ctime(int(time.time())+int(timeout))
        while time.ctime(int(time.time())) < max_time:
            result = self._search_string(str(txt))
            if result:
                return txt
        raise Exception('String "' + txt + '" not found in ' + str(timeout) + ' seconds')

    @keyword(name=None, tags=("Settings",))
    def _search_string(self, string, ignore_case=False):
        """*Search if a string exists on the mainframe screen and return True or False.*
        
        *Arguments*
           
           ``string``: String to be passed 
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
        
         *Examples*
           
               | `Wait Until String` | something |        
        """
        def __read_screen(string, ignore_case):
            for ypos in range(24):
                line = self.mf.string_get(ypos+1, 1, 80)
                if ignore_case: line = line.lower()
                if string in line:
                    logger.debug('String: ' + string + 'found on mainframe screen')
                    return True
            return False
        status = __read_screen(string, ignore_case)
        return status

    @keyword(name=None, tags=("Settings",))
    def page_should_contain_string(self, txt, ignore_case=False, error_message=None):
        """*Search if a given string exists on the mainframe screen. Raised exception can be overridden with error_message*
           
           *Arguments*
           
           ``txt``: String to be searched 
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
            
           
           *Examples*
           
               | `Page Should Contain String` | something |
               | `Page Should Contain String` | someTHING | ignore_case=${True} |
               | `Page Should Contain String` | something | error_message=New error message |
        """
        message = 'The string "' + txt + '" was not found'
        if error_message: message = error_message
        if ignore_case: txt = str(txt).lower()
        result = self._search_string(txt, ignore_case)
        if not result: raise Exception(message)
        logger.info('The string "' + txt + '" was found')

    @keyword(name=None, tags=("Settings",))
    def page_should_not_contain_string(self, txt, ignore_case=False, error_message=None):
        """*Search if a given string NOT exists on the mainframe screen. Raised exception can be overridden with error_message*
           
           *Arguments*
           
           ``txt``: String to be searched 
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
           
           
           *Examples*
           
               | `Page Should Not Contain String` | something |
               | `Page Should Not Contain String` | someTHING | ignore_case=${True} |
               | `Page Should Not Contain String` | something | error_message=New error message |
        """
        message = 'The string "' + txt + '" was found'
        if error_message: message = error_message
        if ignore_case: txt = str(txt).lower()
        result = self._search_string(txt, ignore_case)
        if result: raise Exception(message)

    @keyword(name=None, tags=("Settings",))
    def page_should_contain_any_string(self, list_string, ignore_case=False, error_message=None):
        """*Search if one of the strings in a given list exists on the mainframe screen. Raised exception can be overridden with error_message*
           
           *Arguments*
           
           ``list_string``: List of Strings. Example: ${list_of_string}=    string1        string2  
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
           
           
           *Examples*
           
               | `Page Should Contain Any String` | ${list_of_string} |
               | `Page Should Contain Any String` | ${list_of_string} | ignore_case=${True} |
               | `Page Should Contain Any String` | ${list_of_string} | error_message=New error message |
        """
        message = 'The strings "' + str(list_string) + '" was not found'
        if error_message: message = error_message
        if ignore_case: list_string = [item.lower() for item in list_string]
        for string in list_string:
            result = self._search_string(string, ignore_case)
            if result: break
        if not result: raise Exception(message)

    @keyword(name=None, tags=("Settings",))
    def page_should_not_contain_any_string(self, list_string, ignore_case=False, error_message=None):
        """*Fails if one or more of the strings in a given list exists on the mainframe screen. Raised exception can be overridden with error_message* 
        
        *Arguments*
           
           ``list_string``: List of Strings. Example: ${list_of_string}=    string1        string2  
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
            | `Page Should Not Contain Any Strings` | ${list_of_string} |
            | `Page Should Not Contain Any Strings` | ${list_of_string} | ignore_case=${True} |
            | `Page Should Not Contain Any Strings` | ${list_of_string} | error_message=New error message |
        """
        self._compare_all_list_with_screen_text(list_string, ignore_case, error_message, should_match=False)

    @keyword(name=None, tags=("Settings",))
    def page_should_contain_all_strings(self, list_string, ignore_case=False, error_message=None):
        """*Search if all of the strings in a given list exists on the mainframe screen. Raised exception can be overridden with error_message*
        
        *Arguments*
           
           ``list_string``: List of Strings. Example: ${list_of_string}=    string1        string2  
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
            | `Page Should Contain All Strings` | ${list_of_string} |
            | `Page Should Contain All Strings` | ${list_of_string} | ignore_case=${True} |
            | `Page Should Contain All Strings` | ${list_of_string} | error_message=New error message |
        """
        self._compare_all_list_with_screen_text(list_string, ignore_case, error_message, should_match=True)

    @keyword(name=None, tags=("Settings",))
    def page_should_not_contain_all_strings(self, list_string, ignore_case=False, error_message=None):
        """*Fails if one of the strings in a given list exists on the mainframe screen. Raised exception can be overridden with error_message*
        
        *Arguments*
           
           ``list_string``: List of Strings. Example: ${list_of_string}=    string1        string2  
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True 
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
            | `Page Should Not Contain All Strings` | ${list_of_string} |
            | `Page Should Not Contain All Strings` | ${list_of_string} | ignore_case=${True} |
            | `Page Should Not Contain All Strings` | ${list_of_string} | error_message=New error message |
        """
        message = error_message
        if ignore_case: list_string = [item.lower() for item in list_string]
        for string in list_string:
            result = self._search_string(string, ignore_case)
            if result:
                if message is None:
                    message = 'The string "' + string + '" was found'
                raise Exception(message)

    @keyword(name=None, tags=("Settings",))
    def page_should_contain_string_x_times(self, txt, number, ignore_case=False, error_message=None):
        """*Search if the entered string appears the desired number of times on the mainframe screen. Raised exception can be overridden with error_message*
         
        *Arguments*
           
           ``txt``: String to be matched with 
           
           ``number``: Number of times the string to exist  
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
               | `Page Should Contain String X Times` | something | 3 |
               | `Page Should Contain String X Times` | someTHING | 3 | ignore_case=${True} |
               | `Page Should Contain String X Times` | something | 3 | error_message=New error message |
        """
        message = error_message
        number = int(number)
        all_screen = self._read_all_screen()
        if ignore_case:
            txt = str(txt).lower()
            all_screen = str(all_screen).lower()
        number_of_times = all_screen.count(txt)
        if number_of_times != number:
            if message is None:
                message = 'The string "' + txt + '" was not found "' + str(number) + '" times, it appears "' \
                          + str(number_of_times) + '" times'
            raise Exception(message)
        logger.info('The string "' + txt + '" was found "' + str(number) + '" times')

    @keyword(name=None, tags=("Settings",))
    def page_should_match_regex(self, regex_pattern):
        """*Fails if string does not match pattern as a regular expression.*
        Regular expression check is implemented using the Python [https://docs.python.org/2/library/re.html|re module]. Python's
        regular expression syntax is derived from Perl, and it is thus also very similar to the syntax used,
        for example, in Java, Ruby and .NET.
        Backslash is an escape character in the test data, and possible backslashes in the pattern must
        thus be escaped with another backslash (e.g. \\\d\\\w+).
        """
        page_text = self._read_all_screen()
        if not re.findall(regex_pattern, page_text, re.MULTILINE):
            raise Exception('No matches found for "' + regex_pattern + '" pattern')

    @keyword(name=None, tags=("Settings",))
    def page_should_not_match_regex(self, regex_pattern):
        """*Fails if string does match pattern as a regular expression.* 
        Regular expression check is implemented using the Python [https://docs.python.org/2/library/re.html|re module]. Python's
        regular expression syntax is derived from Perl, and it is thus also very similar to the syntax used,
        for example, in Java, Ruby and .NET.
        Backslash is an escape character in the test data, and possible backslashes in the pattern must
        thus be escaped with another backslash (e.g. \\\d\\\w+).
        """
        page_text = self._read_all_screen()
        if re.findall(regex_pattern, page_text, re.MULTILINE):
            raise Exception('There are matches found for "' + regex_pattern + '" pattern')

    @keyword(name=None, tags=("Settings",))
    def page_should_contain_match(self, txt, ignore_case=False, error_message=None):
        """*Fails unless the given string matches the given pattern. Raised exception can be overridden with error_message*
        Pattern matching is similar as matching files in a shell, and it is always case-sensitive.
        In the pattern, * matches to anything and ? matches to any single character.
        Note that the entire screen is only considered a string for this keyword, so if you want to search
        for the string "something" and it is somewhere other than at the beginning or end of the screen it
        should be reported as follows: **something**
        
        
        *Arguments*
           
           ``txt``: String to be matched with. Can include a pattern. 
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
            | `Page Should Contain Match` | **something** |
            | `Page Should Contain Match` | **so???hing** |
            | `Page Should Contain Match` | **someTHING** | ignore_case=${True} |
            | `Page Should Contain Match` | **something** | error_message=New error message |
        """
        message = error_message
        all_screen = self._read_all_screen()
        if ignore_case:
            txt = txt.lower()
            all_screen = all_screen.lower()
        matcher = Matcher(txt, caseless=False, spaceless=False)
        result = matcher.match(all_screen)
        if not result:
            if message is None:
                message = 'No matches found for "' + txt + '" pattern'
            raise Exception(message)

    @keyword(name=None, tags=("Settings",))
    def page_should_not_contain_match(self, txt, ignore_case=False, error_message=None):
        """*Fails if the given string matches the given pattern. Raised exception can be overridden with error_message*
        Pattern matching is similar as matching files in a shell, and it is always case-sensitive.
        In the pattern, * matches to anything and ? matches to any single character.
        Note that the entire screen is only considered a string for this keyword, so if you want to search
        for the string "something" and it is somewhere other than at the beginning or end of the screen it
        should be reported as follows: **something**
        The search is case sensitive, if you want ignore this you can pass the argument: ignore_case=${True} and you
        can edit the raise exception message with error_message.
        
        *Arguments*
           
           ``txt``: String to be matched with. Can include a pattern. 
           
           ``ignore_case``: Default is Case-sensitive. To ignore case, pass the argument: ignore_case=True
           
           ``error_message``: Override the default message with a new value.
        
        *Examples*
        
            | `Page Should Not Contain Match` | **something** |
            | `Page Should Not Contain Match` | **so???hing** |
            | `Page Should Not Contain Match` | **someTHING** | ignore_case=${True} |
            | `Page Should Not Contain Match` | **something** | error_message=New error message |
        """
        message = error_message
        all_screen = self._read_all_screen()
        if ignore_case:
            txt = txt.lower()
            all_screen = all_screen.lower()
        matcher = Matcher(txt, caseless=False, spaceless=False)
        result = matcher.match(all_screen)
        if result:
            if message is None:
                message = 'There are matches found for "' + txt + '" pattern'
            raise Exception(message)

    @keyword(name=None, tags=("Settings",))
    def _read_all_screen(self):
        """*Read all the mainframe screen and return in a single string.*
        """
        full_text = ''
        for ypos in range(24):
            line = self.mf.string_get(ypos + 1, 1, 80)
            for char in line:
                if char:
                    full_text += char
        return full_text
		
    @keyword(name=None,  tags=("Settings",))
    def login(self, userID, password):
        """*Authenticate to Mainframe*
        
        *Arguments*
           
           ``userID``: AB ID of user with mainframe access
           
           ``password``: Credentail associated to the AB ID of the user
                   
        *Examples*
        
            | `Login` | AB00000 | test1234 |
        """
        logger.debug('Logging In with UserID:' + userID + ' and Password:' + password)
        self._write(userID)
        self.mf.exec_command(b'Tab')	
        self._write(password)
        self._write("Yes", "019", "020")				
        self.mf.send_enter()
        time.sleep(self.wait)
        status = self._search_string("Session Description")
        if status:
            logger.info('Logged In successfully')
        if not status:
            raise Exception('Unable to authenticate for unknown reason, try logging in manually with same credentails')
	
    @keyword(name=None,  tags=("Settings",))
    def choose_session(self, session_id):
        """*Choose the required session by providing sessid*
        
        *Arguments*
           
           ``session_id``: Name of the session in CAPS
                   
        *Examples*
        
            | `Choose Session` | PUCICA8 |
        """
        message = 'Session "' + session_id + '" was not found'
        result, xpos, ypos = self._search_string_and_return_coordinates("_ "+session_id)
        if result:
            logger.debug('Found Session ' + session_id)
            self._write("i", ypos=ypos+1, xpos=xpos+1)
            self.mf.send_enter()
            time.sleep(self.wait)
            status = self._search_string('has ended')
            if status:
                logger.debug('Ended existing session, if any')						
            self._write("s", ypos=ypos+1, xpos=xpos+1)
            self.mf.send_enter()
            time.sleep(self.wait)
            status = self._search_string("Session Description")
            if not status:
                logger.debug('Session ' +session_id + ' selected') 
            
			# Additional check to handle "atso"
            acf_status = self._search_string("ENTER PROC NAME")
            if acf_status:
                logger.debug('Landed on ACF Screen; Entered "atso"')
                self._write("atso")
                self.mf.send_enter()
                self.mf.send_enter()
                self.mf.send_enter()
                time.sleep(self.wait)
				
            login_status = self._search_string("LOGON IN PROGRESS")
            if login_status:
                logger.debug('Landed on Login In Progress Screen')
                self.mf.send_enter()
                time.sleep(self.wait)
                ispf_status = self._search_string("ISPF Primary Option Menu")
                if ispf_status:
                    logger.debug('Landed on ISPF screen')

            logger.info("Session " + session_id + " selected")
			
        if not result: 
            #TODO: Search Next pages until last page and raise exception if session is not found
            raise Exception(message)
        
	
    
    def _search_string_and_return_coordinates(self, string):
        """*Search if the string exists on the mainframe screen and return if True or False along with x and y coordinates.*
           
        """
        def __read_screen_and_return_coordinates(string):
            xpos = 0
            for ypos in range(24):
                line = self.mf.string_get(ypos+1, 1, 80)
                if string in line:
                    logger.debug('The string "' + string + '" was found, returned True, x and y coordinates')
                    xpos = line.index(string)
                    return True, xpos, ypos
            return False, xpos, ypos
        status, xpos, ypos = __read_screen_and_return_coordinates(string)
        return status, xpos, ypos
	
		
    @keyword(name=None,  tags=("Settings",))
    def set_ispf_options(self, ispf_options):
        """*Choose ISPF Primary Menu Options*
        
        *Arguments*
           
           ``ispf_options``: Menu option. For ex: 3.4
                   
        *Examples*
        
            | `Set Ispf Options` | 3.4 |
        """
        ispf_status = self._search_string("ISPF Primary Option Menu")
        if ispf_status:
            self._write(ispf_options)
            self.mf.send_enter()
            time.sleep(self.wait)
            logger.info('ISPF Menu Option ' + ispf_options + ' selected')
            return True
        if not ispf_status:
            logger.info('Cursor not on ISPF screen, cannot set options')
            return False
		
    @keyword(name=None,  tags=("Settings",))
    def search_pds(self, full_qualifier_name):
        """*Search PDS by providing full qualifier name*
        
        *Arguments*
           
           ``full_qualifier_name``: Full qualifier name. For ex: UTILITY.TESTJCL
                   
        *Examples*
        
            | `Search Pds` | UTILITY.TESTJCL |
        """
        # Clear Dsname Level field in Data Set List Utility screen
        self.delete_field("009", "024")
        time.sleep(self.wait)	
        self._write(full_qualifier_name, "009", "024")
        self.mf.send_enter()
        time.sleep(self.wait)
		
		#Exception Handling - throw exception if dataset not found 
        result = self._search_string("No data set names found")
        if result:
            raise Exception('No data set names found for qualifier: "' + full_qualifier_name + '"')		
        
        if not result:
            logger.info("Retrieved dataset: " +full_qualifier_name)

    @keyword(name=None,  tags=("Settings",))
    def view_pds_members(self):
        """*View members of data set*
                          
        *Examples*
        
            | `View Pds Members` | 
        """
        self._write("m", "007", "002")				
        self.mf.send_enter()
        time.sleep(self.wait)

        #Exception Handling 
        result = self._search_string("AUTHORIZATION IS REQUIRED")
        if result:
            raise Exception('DATASET CANNOT BE OPENED; AUTHORIZATION IS REQUIRED')
        if not result:
            logger.info('No authorization issue; assuming pds members are viewed')
            		
			
    @keyword(name=None,  tags=("Settings",))
    def submit_jcl(self, jcl_name=None):
        """*Submit a JCL and returns the JOB ID.*
                          
        *Arguments*
           
           ``jcl_name``: Optional. If not provided, the first job in the list is executed
                   		
		*Examples*
        
            | `Submit Jcl` | 
            | `Submit Jcl` | P2380SFN | 
			| `Submit Jcl` | P2380SFN | 4 | # PF(3) is executed 'x' number of times based on the count provided
        """
        if jcl_name:
            result, xpos, ypos = self._search_string_and_return_coordinates("_ "+jcl_name)
            if result:
                self._write("j", ypos=ypos+1, xpos=xpos+1)
                self.mf.send_enter()
                time.sleep(self.wait)
            if not result:
                raise Exception('JCL "' + jcl_name + '", not found, cannot submit JOB "')					
        
        if jcl_name is None:
            self._write("j", "005", "003")				
            self.mf.send_enter()
            time.sleep(self.wait)
        
        result = self._search_string("SUBMITTED")
        if result:
            logger.info("JOB submitted successfully")
            page_text = self._read_all_screen()
            jobDetails = page_text.partition("JOB")[2]
            jobIDText = jobDetails.partition("JOB")[2]
            jobID = "JOB" + jobIDText[:5]
            logger.info("JOB Details: " +jobDetails) 
            self.mf.send_enter()
            time.sleep(self.wait)
            return jobID
        if not result:
            raise Exception('Something went wrong, JOB cannot be submitted')		
			
    @keyword(name=None,  tags=("Settings",))
    def assert_job_status(self, jobID, max_rc):
        """*Asserts that the return code is expected*
		
		*Arguments*
           
           ``jobID``: JOB ID captured in `Submit Jcl`  
		   
		   ``max_rc``: Expected return code 
           
           ``go_back_count``: Optional. If not provided, cursor lands on ISPF Options Menu Screen
                          
        *Examples*
        
            | `Assert Job Status` | JOB07306 | CC 0000 |
			| `Assert Job Status` | JOB07306 | CC 0000 | 2 |
        """
        ispf_status = self._search_string("ISPF Primary Option Menu")
        if not ispf_status:
            raise Exception('Cannot Assert, cursor not on ISPF menu screen')
        if ispf_status:
            self._write("s;st")				
            self.mf.send_enter()
            time.sleep(self.wait)
            self.mf.send_enter()
            time.sleep(self.wait)			
            totalLines = self.read("003", "068", "2")
            currentLine = self.read("003", "064", "2")
            
            while (currentLine <= totalLines):
        
                status = self._find_jobID_on_screen(jobID)
        
                if status:
                    #TODO: Extract Max-RC Status of JOB
                    result, xpos, ypos = self._search_string_and_return_coordinates(jobID)
                    maxRCReturned = self.read(ypos+1, xpos+9, "11")
                    
                    if max_rc == maxRCReturned.strip():
                        return True
                        
                    if max_rc != maxRCReturned.strip():
                        logger.info('Expected Max-RC "' + max_rc + '", instead found "' + maxRCReturned.strip() + '" ')
                        raise Exception('Assertion Failed, expected and actual max-rc not matching')
                    break
                if not status:
                    self.execute_command("PF(8)")
                    time.sleep(self.wait)
                    newLine = self.read("003", "064", "2")
                    logger.info(newLine)
                    logger.info(currentLine)
                    if newLine == currentLine:
                       raise Exception('Job ID not found in spool')
                    if newLine != currentLine:
                        currentLine = newLine
                    continue            
        
    def _find_jobID_on_screen(self, jobID):
        page_text = self._read_all_screen()
        if jobID in page_text:
            logger.debug('Found JOB ID on screen')
            return True
        if jobID not in page_text:
            return False           

    @keyword(name=None,  tags=("Settings",))
    def return_to_screen(self, screen_identifier, returnKey):
        """*Returns the cursor back to desired screen*
		
		*Arguments*
           
           ``screen_identifier``: Unique Text Identifier on the expected screen. For Ex: ISPF
		   
		   ``returnKey``: Function Key that returns the cursor to previous screen. For Ex: PF(3) 
                          
        *Examples*
        
            | `Return To Screen` | ISPF | PF(3) |
        """
        status = 1
        while (status != 0):
            search_status = self._search_string(screen_identifier)
            if search_status:
                status = 0
                break
            if not search_status:
                self.execute_command(returnKey)
                time.sleep(self.wait)
                continue
				
            
    def _compare_all_list_with_screen_text(self, list_string, ignore_case, message, should_match):
        if ignore_case: list_string = [item.lower() for item in list_string]
        for string in list_string:
            result = self._search_string(string, ignore_case)
            if not should_match and result:
                if message is None:
                    message = 'The string "' + string + '" was found'
                raise Exception(message)
            elif should_match and not result:
                if message is None:
                    message = 'The string "' + string + '" was not found'
                raise Exception(message)

    @staticmethod
    def _check_limits(ypos, xpos):
        """Checks if the user has passed some coordinate y / x greater than that existing in the mainframe
        """
        if int(ypos) > 24:
            raise Exception('You have exceeded the y-axis limit of the mainframe screen')
        if int(xpos) > 80:
            raise Exception('You have exceeded the x-axis limit of the mainframe screen')

