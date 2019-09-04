from session import session_context
import pytest


class SessionDummy(object):
    def __init__(self):
        self.committed = False
        self.rolledback = False
        self.closed = False

    def commit(self):
        if self.committed:
            raise Exception('Already committed')
        self.committed = True

    def rollback(self):
        if self.rolledback:
            raise Exception('Already rolledback')
        self.rolledback = True

    def close(self):
        if self.closed:
            raise Exception('Already closed')
        self.closed = True


def test_transactional_should_commit_and_close_transaction_because_function_executed_successfully(mocker):
    session_context.session = None
    mocker.patch('session.session_context._create_session').return_value = SessionDummy()

    @session_context.transactional
    def method():
        return True

    method()
    assert session_context.session.committed is True
    assert session_context.session.rolledback is False
    assert session_context.session.closed is True


def test_transactional_should_rollback_and_close_transaction_because_function_execution_failed(mocker):
    session_context.session = None
    mocker.patch('session.session_context._create_session').return_value = SessionDummy()

    @session_context.transactional
    def method():
        raise Exception()

    with pytest.raises(Exception):
        method()

    assert session_context.session.committed is False
    assert session_context.session.rolledback is True
    assert session_context.session.closed is True


def test_transactional_should_not_recreate_session_because_another_already_exists(mocker):
    session_context.session = None
    mocker.patch('session.session_context._create_session').return_value = SessionDummy()

    @session_context.transactional
    def method():
        @session_context.transactional
        def sub_method():
            return True
        return sub_method()

    method()
    assert session_context.session.committed is True
    assert session_context.session.rolledback is False
    assert session_context.session.closed is True


def test_get_session_should_return_active_session(mocker):
    session_context.session = None
    mocker.patch('session.session_context._create_session').return_value = SessionDummy()

    @session_context.transactional
    def method():
        session = session_context.get_session()
        assert session is not None
        assert session.committed is False
        assert session.closed is False

    method()
