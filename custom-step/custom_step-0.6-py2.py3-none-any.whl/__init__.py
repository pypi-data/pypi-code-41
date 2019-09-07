# -*- coding: utf-8 -*-

"""
custom_step
A step in a SEAMM flowchart for custom Python
"""

# Bring up the classes so that they appear to be directly in
# the custom_step package.

from custom_step.custom import Custom  # noqa: F401
from custom_step.custom_step import CustomStep  # noqa: F401
from custom_step.tk_custom import TkCustom  # noqa: F401
from custom_step.colourchooser import ColourChooser  # noqa: F401
from custom_step.findwindow import FindWindow  # noqa: F401
from custom_step.fontchooser import FontChooser  # noqa: F401
from custom_step.highlighter import Highlighter  # noqa: F401
from custom_step.linenumbers import LineNumbers  # noqa: F401
from custom_step.textarea import TextArea  # noqa: F401
# from custom_step.texteditor import TextEditor  # noqa: F401

# Handle versioneer
from ._version import get_versions
__author__ = """Paul Saxe"""
__email__ = 'psaxe@molssi.org'
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
