'''
Created on Jun 16, 2014

@author: lwoydziak
'''
from pexpect import EOF, TIMEOUT
from mockito import mock, verify, when, any # http://code.google.com/p/mockito-python/
from dynamic_machine.cli_ssh import SshCli
from mockito.matchers import contains
from _pytest.runner import fail
from dynamic_machine.cli_commands import Root

time = mock()
oneMatch = 1
twoMatches = 2
threeMatches = 3
fourMatches = 4
sixMatches = 6

class TestSshCliCommands():
    def createSshConnection(self, pexpectObject=mock(), user=mock()):
        cli = SshCli("0.0.0.0", user, pexpectObject=pexpectObject)
        cli._secure = True
        cli._connection = mock()
        user.commandLine(cli)
        cli.modeList = [user]
        return cli
    
    def test_index_of_successful_result_received_when_buffering(self):
        cli = self.createSshConnection()
        RANDOM_SUCCESSFUL_RESULT = 201111
        cli.bufferedMode()
        assert cli.compareReceivedAgainst([], indexOfSuccessfulResult=RANDOM_SUCCESSFUL_RESULT) == RANDOM_SUCCESSFUL_RESULT
   
    def test_index_of_result_detected_returned_when_not_buffering(self):
        cli = self.createSshConnection()
        RANDOM_SUCCESSFUL_RESULT = 201111
        when(cli._connection).expect(any(),any(),any()).thenReturn(RANDOM_SUCCESSFUL_RESULT)
        assert cli.compareReceivedAgainst([]) == RANDOM_SUCCESSFUL_RESULT
 
    def test_cli_inspects_console_when_not_buffering(self):
        cli = self.createSshConnection()
        values = ["value1", "value2"]
        cli.compareReceivedAgainst(values)
        verify(cli._connection).expect(values, any(), any())
           
    def test_cli_doesnt_inspect_console_when_buffering(self):
        cli = self.createSshConnection()
        cli.compareReceivedAgainst(["garbage"])
        verify(cli._connection, times=0).expect(any())
  
    def test_cli_can_be_queried_for_buffering(self):
        cli = self.createSshConnection()
        cli.bufferedMode()
        assert cli.buffering()
           
    def test_no_line_is_sent_when_nothing_to_send(self):
        cli = self.createSshConnection()
        cli.flush()
        verify(cli._connection, times=0).sendline(any())
 
    def test_turning_off_buffering_flushes_buffer(self):
        cli = self.createSshConnection()
        cli.bufferedMode()
        cli.send("command1")
        cli.bufferedMode(None)
        verify(cli._connection).sendline("command1")
 
    def test_cli_commands_can_be_batched(self):
        cli = self.createSshConnection()
        cli.bufferedMode()
        cli.send("command1")
        cli.send("command2")
        cli.flush()
        verify(cli._connection).sendline("command1\ncommand2")
           
    def test_cli_send_sends_and_doesnt_buffer_when_in_unbuffered_mode(self):
        cli = self.createSshConnection()
        cli.send("command1")
        verify(cli._connection).sendline("command1")
     
    def test_can_show_output_on_screen(self):
        cli = self.createSshConnection()
        cli.showOutputOnScreen()
        assert cli.trace 
        assert cli.debug
     
    def test_connectingWillSpawnSSH(self):
        pexpectObject = mock()
        cli = self.createSshConnection(pexpectObject)
        when(pexpectObject).spawn(any()).thenReturn(mock())
        cli.connectWithSsh()
        verify(pexpectObject).spawn(contains('ssh'))
         
    def test_connectingFails(self):
        pexpectObject = mock()
        cli = self.createSshConnection(pexpectObject)
        when(pexpectObject).spawn(any()).thenReturn(None)
        try:
            cli.connectWithSsh()
            fail()
        except:
            pass

    def test_modes_cleanedup(self):
        pexpectObject = mock()
        user = mock()
        cli = self.createSshConnection(pexpectObject, user=user)
        when(pexpectObject).spawn(any()).thenReturn(mock())
        cli.connectWithSsh()
        cli._exit_modes_beyond(-1)
        verify(user).exit()
        
    def test_modes_checked(self):
        user = mock()
        user2 = mock()
        cli = self.createSshConnection(user=user)
        cli.modeList = [user, user2]
        cli.check_prereq(0)
        verify(user2).exit()
        
    def test_not_in_right_mode(self):
        cli = self.createSshConnection(user=mock())
        try:
            cli.check_prereq(1)
            fail()
        except:
            pass
        
    def test_can_switch_to_user(self):
        user = mock()
        cli = self.createSshConnection(user=mock())
        cli.execute_as(user)
        verify(user).login()
        
    def test_can_remove_mode(self):
        user = mock()
        cli = self.createSshConnection(user=user)
        cli.exitMode(user)
        assert not len(cli.modeList)
         
    def test_canSetCustomLog(self):
        cli = self.createSshConnection()
        log = "mine"
        cli.resetLoggingTo(log)
        assert cli._connection.logfile == log
         
    def test_setupWithCustomLog(self):
        log = "mine"
        cli = SshCli("0.0.0.0", mock(), log=log)
        cli._connection = mock()
        cli._setupLog()
        assert cli._connection.logfile == log
        
    def test_canFlushLog(self):
        cli = SshCli("0.0.0.0", mock(), trace=True)
        cli._connection = mock()
        cli._setupLog()
        assert not cli._connection.logfile.write(b"")
        assert not cli._connection.logfile.flush()
         
    def test_cannotLogin(self):
        cli = self.createSshConnection(user=Root(password="any"))
        connection = cli._connection
        cli.trace = True
        when(connection).expect(any()).thenReturn(-1)
        cli.debug=True
        try:
            cli.loginSsh()
            fail()
        except:
            pass
        verify(connection).close()
     
    def test_canLogin(self):
        user = mock()
        user.username="username"
        cli = self.createSshConnection(user=user)
        connection = cli._connection
        cli.trace = True
        when(connection).expect(any()).thenReturn(0)
        when(connection).expect(any(), any(), any()).thenReturn(1)
        cli.loginSsh()
        verify(user).sendPassword()
        
    def test_resetingExpectationsDrainsConnectionBuffer(self):
        cli = self.createSshConnection()
        cli._connection.buffer = "something"
        cli._resetExpect()
        assert cli._connection.buffer == ""
        
    def test_lastExpectLooksBeforeAndAfter(self):
        cli = self.createSshConnection()
        cli._connection.before = "something"
        cli._connection.after = "else"
        assert cli._lastExpect() == "somethingelse"
        
    def test_closeAlreadyClosedConnection(self):
        cli = self.createSshConnection()
        cli._connection = None
        cli.closeCliConnectionTo()
        assert (cli._connection == None)

