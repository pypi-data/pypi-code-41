'''
Created on Jun 19, 2014

@author: lwoydziak
'''
import json
import dynamic_machine.cli_commands
from dynamic_machine.cli_commands import Command, User
from dynamic_machine.cli_ssh import SshCli
from builtins import RuntimeWarning, Exception

class CliProcessingJson(object):
    '''
    classdocs
    
    JSON should be of the format:
    {
        "hostname" : "<ip>"
        "username" : "root"
        "password" : None #if using ssh cert
        "commands" : [ # in order of desire issuance
            {"ls"   : { "dontCareAboutResult"    : None }},
            {"pwd"  : { "assertResultEquals"     : "/home/user" }},
            {"cd /" : { "assertResultNotEquals"  : ["Permission Denied",30]}},
        ]
    }
    '''


    def __init__(self, jsonFileName, initialJsonString=None, jsonObject=None):
        self.__jsonObject = json if not jsonObject else jsonObject
        self.__jsonFileName = jsonFileName
        self.__json = self.__jsonObject.loads(initialJsonString) if initialJsonString else None
        
    def loadJsonFile(self):
        jsonFile = None
        try:
            jsonFile = open(self.__jsonFileName, "r")
        except Exception as e:
            print(str(e))
            pass
        
        try:
            self.__json = self.__jsonObject.load(jsonFile)
        except Exception as e:
            print(str(e))
            return

    def getCommand(self, name, expectation):
        expectationName = list(expectation.keys())[0]
        expectationObject = getattr(dynamic_machine.cli_commands,expectationName)
        expectationValue = expectation[expectationName]
        if not expectationValue:
            return Command(name, expectationObject())
        elif isinstance(expectationValue, list):
            return Command(name, expectationObject(*expectationValue))
        else:
            return Command(name, expectationObject(expectationValue))
    
    def execute(self, UserObject=User, CliObject=SshCli):
        if not self.__json:
            raise RuntimeError("Json not yet defined so cannot execute!")
        
        user = UserObject(self.__json['username'], self.__json['password'])
        cli = CliObject(self.__json["hostname"], user, debug=True, trace=True)
        try:
            cli.connectWithSsh()
            cli.loginSsh()
        except Exception as e:
            raise RuntimeWarning("Unable to Login: "+str(e))
        
        try:
            for aJsonCommand in self.__json['commands']:
                commandName = list(aJsonCommand.keys())[0]
                print("----------------------------------------------------------------------------------------- Trying: "+commandName)
                command = self.getCommand(commandName, aJsonCommand[commandName])
                user.execute([command])
        except KeyError:
            pass
            
        cli.closeCliConnectionTo()
    
    