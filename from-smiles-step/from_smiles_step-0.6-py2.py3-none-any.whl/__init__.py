# -*- coding: utf-8 -*-

"""
from_smiles_step
A step for generating a structure from a SMILES string.
"""

# Bring up the classes so that they appear to be directly in
# the package.

from from_smiles_step.from_smiles_step import FromSMILESStep  # noqa: F401
from from_smiles_step.from_smiles import FromSMILES  # noqa: F401
from from_smiles_step.from_smiles_parameters import FromSMILESParameters  # noqa: F401 E501
from from_smiles_step.tk_from_smiles import TkFromSMILES  # noqa: F401

# Handle versioneer
from ._version import get_versions
__author__ = """Paul Saxe"""
__email__ = 'psaxe@molssi.org'
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
