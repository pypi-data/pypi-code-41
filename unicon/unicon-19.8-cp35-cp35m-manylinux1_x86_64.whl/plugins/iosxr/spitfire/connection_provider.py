__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "Sritej K V R <skanakad@cisco.com>"



from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider,IOSXRDualRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxr.spitfire.statements import connection_statement_list 



class SpitfireSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
    
    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.SPITFIRE_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.SPITFIRE_INIT_CONFIG_COMMANDS


    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        return Dialog(connection_statement_list)

class SpitfireDualRpConnectionProvider(IOSXRDualRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
    
    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.SPITFIRE_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.SPITFIRE_INIT_CONFIG_COMMANDS


    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        return Dialog(connection_statement_list)

