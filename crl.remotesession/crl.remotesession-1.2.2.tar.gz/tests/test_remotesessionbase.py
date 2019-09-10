__copyright__ = 'Copyright (C) 2019, Nokia'


def test_get_remoterunner(remotesession,
                          mock_remoterunner):
    assert remotesession.get_remoterunner() == mock_remoterunner.return_value


def test_close(mock_remoterunner,
               remotesession):
    remotesession.close()
    mock_remoterunner.return_value.close.assert_called_once_with()
