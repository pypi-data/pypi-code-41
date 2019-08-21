"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.
Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

from invoke import task
import pytest


@task
def full(ctx):
    """
    Run The Full Test Suite
    """
    pytest.main(['tests'])


@task
def unit(ctx):
    """
    Run Unit Tests
    """
    pytest.main(['tests'])


@task
def func(ctx):
    """
    Run Functional Tests
    """
    pytest.main(['tests'])


@task
def sub(ctx):
    """
    Run Subcutaneous Tests
    """
    pytest.main(['tests'])
