# -*- coding: utf-8 -*-
"""a node to create a structure from a SMILES string"""

import from_smiles_step
import logging
import seamm
import seamm.data
import seamm_util
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __
import pprint

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter('from_smiles')


class FromSMILES(seamm.Node):
    def __init__(self, flowchart=None, extension=None):
        '''Initialize a specialized start node, which is the
        anchor for the graph.

        Keyword arguments:
        '''
        logger.debug('Creating FromSMILESNode {}'.format(self))

        super().__init__(flowchart=flowchart, title='from SMILES',
                         extension=extension)

        self.parameters = from_smiles_step.FromSMILESParameters()

    @property
    def version(self):
        """The semantic version of this module.
        """
        return from_smiles_step.__version__

    @property
    def git_revision(self):
        """The git version of this module.
        """
        return from_smiles_step.__git_revision__

    def description_text(self, P=None):
        """Return a short description of this step.

        Return a nicely formatted string describing what this step will
        do.

        Keyword arguments:
            P: a dictionary of parameter values, which may be variables
                or final values. If None, then the parameters values will
                be used as is.
        """

        if not P:
            P = self.parameters.values_to_dict()

        if P['smiles string'][0] == '$':
            text = (
                "Create the structure from the SMILES in the variable"
                " '{smiles string}'."
            )
        else:
            text = "Create the structure from the SMILES '{smiles string}'"

        if isinstance(P['minimize'], bool) and P['minimize']:
            text += "The structure will be minimized"
            text += " with the '{forcefield}' forcefield."
        elif isinstance(P['minimize'], str) and P['minimize'][0] == '$':
            text += "The structure will be minimized if '{minimize}' is true"
            text += " with the '{forcefield}' forcefield."

        return self.header + '\n' + __(
            text, **P, indent=4 * ' '
        ).__str__()

    def run(self):
        """Create 3-D structure from a SMILES string

        The atom ordering is a problem, since SMILES keeps hydrogens
        implicitly, so they tend to be added after the heavy atoms. If
        we keep them explicitly, for instance by tricking SMILES by
        using At for H, then the atom order is changed, which is not
        good.

        To avoid this we will use explict H's (labeled as At's). Since
        OpenBabel will not directly convert SMILES to SMILES with
        explicit H's, we use a molfile as an intermediate.

        Equivalent command line is like: ::
            echo 'CCO' | obabel --gen3d -ismi -omol | obabel -imol -osmi -xh\
                  | obabel --gen3d -ismi -opcjson
        """

        next_node = super().run(printer)

        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Print what we are doing
        printer.important(self.description_text(P))

        if P['smiles string'] is None or P['smiles string'] == '':
            return None

        local = seamm.ExecLocal()
        smiles = P['smiles string']

        result = local.run(
            cmd=['obabel', '--gen3d', '-ismi', '-omol'],
            input_data=smiles
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            seamm.data.structure = None
            return None

        logger.debug('***Intermediate molfile from obabel')
        logger.debug(result['stdout'])

        mol = result['stdout']
        result = local.run(
            cmd=['obabel', '-imol', '-osmi', '-xh'],
            input_data=mol
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            seamm.data.structure = None
            return None

        smiles = result['stdout']
        logger.debug('***smiles with Hs from obabel')
        logger.debug(smiles)

        if P['minimize']:
            # from SMILES to mol2
            result = local.run(
                cmd=['obabel', '--gen3d', '-ismi', '-omol2'],
                input_data=smiles
            )

            # logger.log(0, pprint.pformat(result))
            logger.debug('***Intermediate mol2 file from obabel')
            logger.debug(result['stdout'])

            if int(result['stderr'].split()[0]) == 0:
                seamm.data.structure = None
                return None

            files = {}
            files['input.mol2'] = result['stdout']

            # minimize
            result = local.run(
                cmd=['obminimize', '-o', 'mol2',
                     '-ff', P['forcefield'], 'input.mol2'],
                files=files
            )

            # logger.log(0, pprint.pformat(result))
            logger.debug('***Intermediate mol2 from obminimize')
            logger.debug(result['stdout'])
            mol2 = result['stdout']

            result = local.run(
                cmd=['obabel', '-imol2', '-omol', '-x3'],
                input_data=mol2
            )
            if int(result['stderr'].split()[0]) == 0:
                seamm.data.structure = None
                return None

            structure = seamm_util.molfile.to_seamm(result['stdout'])
        else:
            result = local.run(
                cmd=['obabel', '--gen3d', '-ismi', '-omol', '-x3'],
                input_data=smiles
            )

            logger.log(0, pprint.pformat(result))

            if int(result['stderr'].split()[0]) == 0:
                seamm.data.structure = None
                return None

            logger.debug('***Structure from obabel')
            logger.debug(result['stdout'])

            structure = seamm_util.molfile.to_seamm(result['stdout'])

        structure['periodicity'] = 0
        units = structure['units'] = {}
        units['coordinates'] = 'angstrom'

        seamm.data.structure = structure

        logger.debug('\n***Structure dict')
        logger.debug(pprint.pformat(structure))

        # Finish the output
        printer.important(
            __("    Created a molecular structure with {n_atoms} atoms.\n",
               n_atoms=len(structure['atoms']['elements']),
               indent='    ')
        )
        printer.important('')

        return next_node
