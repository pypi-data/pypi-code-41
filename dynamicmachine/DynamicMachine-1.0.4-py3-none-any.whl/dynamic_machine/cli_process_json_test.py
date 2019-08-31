'''
Created on Jun 19, 2014

@author: lwoydziak
'''
from dynamic_machine.cli_process_json import CliProcessingJson
from mockito.mocking import mock
from mockito.matchers import any
from mockito.mockito import when, verifyNoMoreInteractions, verify
from _pytest.runner import fail
from dynamic_machine.cli_commands import Command
from json import dumps, loads

def test_constructionWithInitialJson():
    CliProcessingJson("garbage", '{"none":"none"}')

def test_successfullLoadFromFile():
    jsonObject = mock()
    cliProcessingJson = CliProcessingJson("garbage", jsonObject=jsonObject)
    when(jsonObject).load(any()).thenReturn({})
    cliProcessingJson.loadJsonFile()
    verify(jsonObject).load(any())
    
def test_unsuccessfullLoadFromFile():
    jsonObject = mock()
    cliProcessingJson = CliProcessingJson("garbage", jsonObject=jsonObject)
    when(jsonObject).load(any()).thenRaise(Exception())
    cliProcessingJson.loadJsonFile()
    
def test_commandCreatedCorrectly():
    cliProcessingJson = CliProcessingJson("garbage")
    assert 'pwd' in str(cliProcessingJson.getCommand("pwd", {"dontCareAboutResult":None}).__dict__)
    assert 'dontCareAboutResult' in str(cliProcessingJson.getCommand("pwd", {"dontCareAboutResult":None}).__dict__)
    
def test_commandCreatedCorrectlyWhenAssertingResults():
    cliProcessingJson = CliProcessingJson("garbage")
    assert 'assertResultEquals'  in str(cliProcessingJson.getCommand("pwd", {"assertResultEquals":"/home/user"}).__dict__)

def test_commandCreatedCorrectlyWithTimeout():
    cliProcessingJson = CliProcessingJson("garbage")
    sample = {"assertResultEquals":("result", 60)}
    string = dumps(sample)
    json = loads(string)
    assert "'_seconds': 60"  in str(cliProcessingJson.getCommand("pwd", json).expectation._timeout.__dict__)
    
def test_executingWithNoJsonRaises():
    cliProcessingJson = CliProcessingJson("garbage")
    try:
        cliProcessingJson.execute()
        fail()
    except:
        pass

def setupCliProcessingJson(json, password=None):
    cliProcessingJson = CliProcessingJson("garbage", initialJsonString=json)
    UserObject = mock()
    user = mock()
    user.password = password
    CliObject = mock()
    cli = mock()
    when(UserObject).called(any(), any()).thenReturn(user)
    when(CliObject).called(any(), any(), debug=any(), trace=any()).thenReturn(cli)
    return cliProcessingJson, UserObject, CliObject, cli, user

def test_excutingWithNoCommandsJustLogsIn():
    json = '{\
        "hostname" : "<ip>",\
        "username" : "root",\
        "password" : null\
    }'
    cliProcessingJson, UserObject, CliObject, cli, user = setupCliProcessingJson(json)
    cliProcessingJson.execute(UserObject.called, CliObject.called)
    verify(cli).connectWithSsh()
    verify(cli).closeCliConnectionTo()
    verifyNoMoreInteractions(user)
    
def test_excutingWithPasswordUsesPassword():
    json = '{\
        "hostname" : "<ip>",\
        "username" : "root",\
        "password" : "password"\
    }'
    cliProcessingJson, UserObject, CliObject, cli, _ = setupCliProcessingJson(json, "password")
    cliProcessingJson.execute(UserObject.called, CliObject.called)
    verify(cli, atleast=1).loginSsh()
    
def test_canExecuteCommand():
    json = '{\
        "hostname" : "<ip>",\
        "username" : "root",\
        "password" : null,\
        "commands" : [ \
            {"ls"   : { "dontCareAboutResult"    : null}},\
            {"pwd"  : { "assertResultEquals"     : "/home/user"}},\
            {"cd /" : { "assertResultNotEquals"  : "Permission Denied"}}\
        ]\
    }'
    cliProcessingJson, UserObject, CliObject, _, user = setupCliProcessingJson(json, "password")
    cliProcessingJson.execute(UserObject.called, CliObject.called)
    verify(user, times=3).execute(any())
    
def test_raiseWhenSshConnectionFails():
    json = '{\
        "hostname" : "<ip>",\
        "username" : "root",\
        "password" : "password"\
    }'
    cliProcessingJson, UserObject, CliObject, cli, _ = setupCliProcessingJson(json, "password")
    when(cli).loginSsh().thenRaise(Exception("Any"))
    try:
        cliProcessingJson.execute(UserObject.called, CliObject.called)
        fail()
    except:
        pass
    