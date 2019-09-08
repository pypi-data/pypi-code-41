# -*- coding: utf-8 -*-
"""Main class for handling forcefields"""

import logging
from PIL import ImageTk
import rdkit
import rdkit.Chem
import rdkit.Chem.Draw
import rdkit.Chem.AllChem
import re
import tkinter as tk

logger = logging.getLogger(__name__)


class FFAssigner(object):
    def __init__(self, forcefield, have_tk=False):
        """Handle the assignment of the forcefield to the structure

        This class is closely related to the Forcefield class, but
        separated from it due to the dependencies it carries along,
        coupled with the fact that it is not needed in some
        computations where the forcefield itself is.
        """

        self.forcefield = forcefield
        self.have_tk = have_tk

    def assign(self, smiles=None, add_hydrogens=True):
        """Assign the atom types to the structure using SMARTS templates
        """
        if smiles is None:
            raise RuntimeError(
                "Cannot assign the forcefield without a structure!")

        logger.debug("SMILES = '{}'".format(smiles))

        # temporarily handle explicit hydrogens

        pat3 = re.compile('H3\]')  # noqa: W605
        pat2 = re.compile('H2\]')  # noqa: W605
        pat1 = re.compile('(?P<c1>[^[])H\]')  # noqa: W605

        smiles = pat3.sub(']([H])([H])([H])', smiles)
        smiles = pat2.sub(']([H])([H])', smiles)
        smiles = pat1.sub('\g<c1>]([H])', smiles)  # noqa: W605

        h_subst = None
        for el in ('Rb', 'Cs', 'Fr', 'At'):
            if el not in smiles:
                h_subst = el
                pat4 = re.compile('\[H\]')  # noqa: W605
                smiles = pat4.sub('[{}]'.format(el), smiles)
                logger.debug("Subst SMILES = '{}'".format(smiles))
                break

        molecule = rdkit.Chem.MolFromSmiles(smiles)
        if molecule is None:
            print("There was problem with the SMILES '{}'".format(smiles))
            return

        if h_subst is not None:
            for atom in molecule.GetAtoms():
                if atom.GetSymbol() == h_subst:
                    atom.SetAtomicNum(1)

        if add_hydrogens:
            molecule = rdkit.Chem.AddHs(molecule)
            n_atoms = molecule.GetNumAtoms()
            logger.debug("'{}' has {} atoms with hydrogens added".format(
                smiles, n_atoms))
        else:
            n_atoms = molecule.GetNumAtoms()
            logger.debug("'{}' has {} atoms".format(smiles, n_atoms))

        atom_types = ['?'] * n_atoms
        templates = self.forcefield.get_templates()
        for atom_type in templates:
            template = templates[atom_type]
            for smarts in template['smarts']:
                pattern = rdkit.Chem.MolFromSmarts(smarts)

                ind_map = {}
                for atom in pattern.GetAtoms():
                    map_num = atom.GetAtomMapNum()
                    if map_num:
                        ind_map[map_num - 1] = atom.GetIdx()
                map_list = [ind_map[x] for x in sorted(ind_map)]

                matches = molecule.GetSubstructMatches(pattern)
                logger.debug(atom_type + ': ')
                if len(matches) > 0:
                    for match in matches:
                        atom_ids = [match[x] for x in map_list]
                        for x in atom_ids:
                            atom_types[x] = atom_type
                        tmp = [str(x) for x in atom_ids]
                        logger.debug('\t' + ', '.join(tmp))

        i = 0
        untyped = []
        for atom, atom_type in zip(molecule.GetAtoms(), atom_types):
            if atom_type == '?':
                untyped.append(i)
            logger.debug("{}: {}".format(atom.GetSymbol(), atom_type))
            i += 1

        if len(untyped) > 0:
            logger.warning('The forcefield does not have atom types for'
                           ' the molecule!. See missing_atom_types.png'
                           ' for more detail.')
            tmp = rdkit.Chem.AllChem.Compute2DCoords(molecule)
            img = rdkit.Chem.Draw.MolToImage(molecule,
                                             size=(1000, 1000),
                                             highlightAtoms=untyped,
                                             highlightColor=(0, 1, 0))
            img.save('missing_atom_types.png')

            if self.have_tk:
                root = tk.Tk()
                root.title('Atom types')
                tkPI = ImageTk.PhotoImage(img)
                tkLabel = tk.Label(root, image=tkPI)
                tkLabel.place(x=0, y=0, width=img.size[0], height=img.size[1])
                root.geometry('%dx%d' % (img.size))
                root.mainloop()
        else:
            logger.info('The molecule was successfully atom-typed')

        return atom_types
