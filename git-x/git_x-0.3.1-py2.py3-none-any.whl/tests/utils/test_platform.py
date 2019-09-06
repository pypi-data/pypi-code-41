import pytest
import os
import sys
import mock
from utils import *


@mock.patch('sys.platform', 'win32')
def test_is_windows():
    assert Platform.is_windows() == True
    assert Platform.is_mac() == False
    assert Platform.is_linux() == False
    assert Platform.is_cygwin() == False


@mock.patch('sys.platform', 'darwin')
def test_is_mac():
    assert Platform.is_windows() == False
    assert Platform.is_mac() == True
    assert Platform.is_linux() == False
    assert Platform.is_cygwin() == False


@mock.patch('sys.platform', 'linux')
def test_is_linux():
    assert Platform.is_windows() == False
    assert Platform.is_mac() == False
    assert Platform.is_linux() == True
    assert Platform.is_cygwin() == False


@mock.patch('sys.platform', 'cygwin')
def test_is_cygwin():
    assert Platform.is_windows() == False
    assert Platform.is_mac() == False
    assert Platform.is_linux() == False
    assert Platform.is_cygwin() == True
