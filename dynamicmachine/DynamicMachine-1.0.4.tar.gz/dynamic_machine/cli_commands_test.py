'''
Created on Jun 17, 2014

@author: lwoydziak
'''
from pexpect import EOF, TIMEOUT
from mockito.mocking import mock
from mockito.mockito import when, verify
from dynamic_machine.cli_commands import Mode, Command, assertResultNotEquals,\
    assertResultEquals, dontCareAboutResult, beforeSeconds, ResultOperations,\
    User
from mockito.matchers import any, contains
from _pytest.runner import fail

class TestCliCommands():
    def makeCli(self):
        cli = mock()
        cli._connection = mock()
        cli.modeList = mock()
        return cli
    
    def test_mode_executed_with_multiple_commands(self):
        cli = self.makeCli()
        testMode = Mode(cli)
        command1 = mock()
        command2 = mock()
         
        testMode.execute([
                command1,
                command2
                ])
     
        verify(command1).executeOn(cli)
        verify(command2).executeOn(cli)

    def test_mode_exited(self):
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any()).thenReturn(0)
        testMode = Mode(cli)
        testMode.exit()
        verify(cli).exitMode(testMode)
        verify(cli).send("exit")

    def test_command_excuted_correctly(self):
        mockCommand = "Mock"
        expectation = mock()
        cli = self.makeCli()
         
        testCommand = Command(mockCommand, expectation)
        testCommand.executeOn(cli)
         
        verify(cli).send(mockCommand)
        verify(expectation).executeOn(cli)
     
    def test_no_assertion_when_bad_result_not_detected(self):
        resultDoesNotContainBadResult = 1
        badResult = "who cares"
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(), any(), indexOfSuccessfulResult=any()).thenReturn(resultDoesNotContainBadResult)
         
        assertion = assertResultNotEquals(badResult)
        assertion.executeOn(cli)
         
        verify(cli).compareReceivedAgainst([badResult, "$", EOF, TIMEOUT], any(), indexOfSuccessfulResult=any())
 
    def test_assertion_when_bad_result_detected(self):
        resultContainBadResult = 0
        badResult = "who cares"
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any(), indexOfSuccessfulResult=any()).thenReturn(resultContainBadResult)
         
        assertion = assertResultNotEquals(badResult)
        try:
            assertion.executeOn(cli)
            fail()
        except:
            pass
         
        verify(cli).compareReceivedAgainst([badResult, "$", EOF, TIMEOUT], any(), indexOfSuccessfulResult=any())
     
    def test_good_result_is_used_when_set_for_assertion_of_bad_result(self):
        resultDoesNotContainBadResult = 1
        badResult = "who cares"
        acceptableResult = "I want this"
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any(), indexOfSuccessfulResult=any()).thenReturn(resultDoesNotContainBadResult)
         
        resultNot_badResult = assertResultNotEquals(badResult).butCanBe(acceptableResult)
        resultNot_badResult.executeOn(cli)
         
        verify(cli).compareReceivedAgainst([badResult, acceptableResult, EOF, TIMEOUT], any(), indexOfSuccessfulResult=resultDoesNotContainBadResult)
     
    def test_no_assertion_when_good_result_detected(self):
        resultContainGoodResult = 0
        goodResult = "who cares"
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any(),indexOfSuccessfulResult=any()).thenReturn(resultContainGoodResult)
         
        assertion = assertResultEquals(goodResult)
        assertion.executeOn(cli)
         
        verify(cli).compareReceivedAgainst([goodResult, EOF, TIMEOUT], any(),indexOfSuccessfulResult=0)
     
    def test_no_assertion_because_dontCareAboutResult(self):
        cli = self.makeCli()
        assertion = dontCareAboutResult()
        assertion.executeOn(cli)

    def test_beforeSeconds_returns_seconds(self):
        assert (30 == beforeSeconds(30).value())
        
    def test_command_equals_command(self):
        commandOne = Command("test", dontCareAboutResult())
        commandTwo = Command("test" , dontCareAboutResult())
        assert(commandOne == commandTwo)
        assert(commandOne != 1)
        commandTwo.expectation = assertResultNotEquals("")
        assert(commandOne != commandTwo)
        commandTwo.commandName = "notTest"
        assert(commandOne != commandTwo)
         
    def test_dontCareAboutResult_equals_dontCareAboutResult(self):
        assertionOne = dontCareAboutResult()
        assertionTwo = dontCareAboutResult()
        assert (assertionOne == assertionTwo)
        assert (assertionOne != 1)
         
    def test_assertResultNotEquals_not_equals_assertResultNotEquals(self):
        assertionOne = assertResultNotEquals("test")
        assertionTwo = assertResultNotEquals("not equal")
        assert(assertionOne != assertionTwo)
        assert(assertionOne != 1)
         
    def test_assertResultNotEquals_equals_assertResultNotEquals(self):
        assertionOne = assertResultNotEquals("test")
        assertionTwo = assertResultNotEquals("test")
        assert(assertionOne == assertionTwo)
        assertionTwo.butCanBe("newAcceptableResult")
        assert(assertionOne != assertionTwo)
         
    def test_assertResultEquals_not_equals_assertResultEquals(self):
        assertionOne = assertResultEquals("test")
        assertionTwo = assertResultEquals("not equal")
        assert(assertionOne != assertionTwo)
        assert(assertionOne != 1)
         
    def test_assertResultEquals_equals_assertResultEquals(self):
        assertionOne = assertResultEquals("test")
        assertionTwo = assertResultEquals("test")
        assert(assertionOne == assertionTwo)
        
    def test_ResultOperations_equals_ResultOperations(self):
        ro1 = ResultOperations()
        ro2 = ResultOperations()
        assert(ro1 == ro2)
        assert(ro1 != 1)
         
    def test_no_assertion_when_good_results_detected(self):
        resultContainGoodResult = 1
        goodResult = ["who cares", "I don't"]
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any(), indexOfSuccessfulResult=any()).thenReturn(resultContainGoodResult)
         
        assertion = assertResultEquals(goodResult)
        assertion.executeOn(cli)
         
        verify(cli).compareReceivedAgainst(goodResult+[EOF, TIMEOUT], any(), indexOfSuccessfulResult=0)
 
    def test_assertion_when_good_results_not_detected(self):
        resultDoesNotContainGoodResult = 2
        goodResult = ["who cares", "I don't"]
        cli = self.makeCli()
        when(cli).compareReceivedAgainst(any(),any(), indexOfSuccessfulResult=any()).thenReturn(resultDoesNotContainGoodResult)
         
        assertion = assertResultEquals(goodResult)
        try: 
            assertion.executeOn(cli)
            fail()
        except:
            pass
         
        verify(cli).compareReceivedAgainst(goodResult+[EOF, TIMEOUT], 30, indexOfSuccessfulResult=0)
        
    def test_user_can_login_with_password(self):
        cli = mock()
        user = User("username", "password", cli)
        when(cli).compareReceivedAgainst(any(),any(), indexOfSuccessfulResult=any()).thenReturn(0).thenReturn(1)
        user.login()
        verify(cli).send("su username")
        verify(cli).send("password")
        
 