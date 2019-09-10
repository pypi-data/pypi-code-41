# -*- coding: utf-8 -*-

"""Helper class needed for the stevedore integration. Needs to provide
a description() method that returns a dict containing a description of
this node, and a factory() method for creating the graphical and non-graphical
nodes."""

import from_smiles_step


class FromSMILESStep(object):
    my_description = {
        'description':
            'Creates a 3D molecular structure from a SMILES string.',
        'group':
            'Building',
        'name':
            'from SMILES'
    }

    def __init__(self, flowchart=None, gui=None):
        """Initialize this helper class, which is used by
        the application via stevedore to get information about
        and create node objects for the flowchart
        """
        pass

    def description(self):
        """Return a description of what this extension does
        """
        return FromSMILESStep.my_description

    def create_node(self, flowchart=None, **kwargs):
        """Return a new node object"""
        return from_smiles_step.FromSMILES(flowchart=flowchart, **kwargs)

    def create_tk_node(self, canvas=None, **kwargs):
        """Return the graphical Tk node object"""
        return from_smiles_step.TkFromSMILES(canvas=canvas, **kwargs)
