'''
Created on Jun 17, 2014

@author: lwoydziak
'''
from pexpect import EOF, TIMEOUT

class beforeSeconds:
    def __init__(self, seconds):
        self._seconds = seconds
#     def __class__(self): # allow for callback type execution, most not needed
#         return self
    def value(self):
        return self._seconds

class ResultOperations(object):
    def __init__(self, timeout=None):
        if not timeout:
            self._timeout = beforeSeconds(30)
        else:
            self._timeout = timeout if isinstance(timeout, beforeSeconds) else beforeSeconds(timeout)
    
    def executeOn(self, cli):
        pass
    
    def __eq__(self, object):
        if not isinstance(object, ResultOperations):
            return False
        return True
    
    def _concatenate(self, target, withList):
        if isinstance(withList, list):
            target.extend(withList)
        else:
            target.append(withList)
        return target

class dontCareAboutResult(ResultOperations):
#     def __class__(self):
#         return self
    
    def __eq__(self, object):
        if not isinstance(object, dontCareAboutResult):
            return False
        return True

class assertResultNotEquals(ResultOperations):
    def __init__(self, unexpectedResult, timeout=None):
        super(assertResultNotEquals, self).__init__(timeout)
        self.unexpectedResult = unexpectedResult
        self._acceptableResult = None
    
#     def __class__(self):
#         return self
          
    def __eq__(self, object):
        if not isinstance(object, assertResultNotEquals):
            return False
        if not self.unexpectedResult == object.unexpectedResult:
            return False
        if not self._acceptableResult == object._acceptableResult:
            return False
        return True
    
    def butCanBe(self, newAcceptableResult):
        self._acceptableResult = newAcceptableResult
        return self
        
    def expectation(self):
        expectation = self._concatenate([], self.unexpectedResult)
        expectation = self._concatenate(expectation, self._acceptableResult)
        expectation.append(EOF)
        expectation.append(TIMEOUT)
        return expectation
    
    def executeOn(self, cli):
        super(assertResultNotEquals, self).executeOn(cli)
        if not self._acceptableResult:
            self._acceptableResult = "$"
        expectation = self.expectation()
        position = cli.compareReceivedAgainst(expectation, self._timeout.value(), indexOfSuccessfulResult=len(expectation)-3)
        if position < len(self._concatenate([], self.unexpectedResult)) or position >= len(expectation)-2:
            raise Exception(self.unexpectedResult + "!" + "\nWhile executing: " + cli._lastExpect())
        
class assertResultEquals(ResultOperations):
    def __init__(self, expectedResult, timeout=None):
        super(assertResultEquals, self).__init__(timeout)
        self.expectedResult = expectedResult
    
    def __eq__(self, object):
        if not isinstance(object, assertResultEquals):
            return False
        if not self.expectedResult == object.expectedResult:
            return False
        return True
    
#     def __class__(self):
#         return self
    
    def executeOn(self, cli):
        super(assertResultEquals, self).executeOn(cli)
        expectation = self._concatenate([], self.expectedResult)
        expectation.append(EOF)
        expectation.append(TIMEOUT)
        i = cli.compareReceivedAgainst(expectation, self._timeout.value(), indexOfSuccessfulResult=0)
        if i >= len(expectation)-2:
            raise Exception(self.expectedResult + " not found ("+str(i)+")!" + "\nWhile executing: " + cli._lastExpect() )


class Command(object):
    def __init__(self, commandName, expectation):
        self.commandName = commandName
        self.expectation = expectation

#     def __class__(self):
#         return self
    
    def __eq__(self, object):
        if not isinstance(object, Command):
            return False
        if not self.commandName == object.commandName:
            return False
        if not self.expectation == object.expectation:
            return False
        return True
        
    def executeOn(self, cli):
        cli.send(self.commandName)
        cli._resetExpect()
        self.expectation.executeOn(cli)

class Mode(object):
    def __init__(self, cli):
        self._cli = cli
        self._exitCommand = Command("exit", dontCareAboutResult())
        
#     def __class__(self):
#         return self

    def execute(self, commands):
        for command in commands:
            command.executeOn(self._cli)

    def exit(self):
        self._cli.exitMode(self)
        self._exitCommand.executeOn(self._cli)
        
class User(Mode):
    def __init__(self, username, password, cli=None):
        super(User, self).__init__(cli)
        self.username = username
        self.password = password
        self._prompt = username + "@"
        self._usernameSent=False
        
    def sendPassword(self):
        if not self.password == "" and not self._usernameSent: # because they could use an ssh key
            assertResultEquals('password:').executeOn(self._cli)
        
        resultNotPermissionDenied = assertResultNotEquals("Permission denied")
        resultNotPermissionDenied.butCanBe([self._prompt])
        Command(self.password, resultNotPermissionDenied).executeOn(self._cli)
    
    def sendUsername(self):
        Command("su "+self.username, assertResultEquals("Password:")).executeOn(self._cli)
        self._usernameSent=True
    
    def commandLine(self, cli):
        self._cli=cli
        
    def login(self):
        self.sendUsername()
        self.sendPassword()
        
#     def __class__(self):
#         super(Root, self).__call__()
#         return self
        
class Root(User):
    USERNAME = 'root'
    
    def __init__(self, password, cli=None):
        super(Root, self).__init__(self.USERNAME, password, cli)
