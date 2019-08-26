"""Run test functions for essential_align_mod.py module."""
import essential_align_mod as essential
from typing import Dict, List
import os
import sys
import pickle
# import Cython module for remapping headers
#from sonicparanoid import remap_tables_c as remap


'''
def test_remap_pairwise_relations(debug=False) -> None:
    """Test the remapping of FASTA headers."""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/remap_test')
    print(testRoot)
    inTbl = os.path.join(testRoot, "table.1-2")
    outTbl = os.path.join(testRoot, "output/1-2")

    # load hdr mapping dictionary
    mappingPicklPath1 = os.path.join(testRoot, "hdr_1.pckl")
    with open(mappingPicklPath1, "rb") as fd:
        old2NewHdrDictA = pickle.load(fd)

    mappingPicklPath2 = os.path.join(testRoot, "hdr_2.pckl")
    with open(mappingPicklPath2, "rb") as fd:
        old2NewHdrDictB = pickle.load(fd)

    remap.remap_pairwise_relations(
        inTbl, outTbl, old2NewHdrDictA, old2NewHdrDictB, debug=debug)
'''

def main() -> int:

    # call info function
    essential.info()

    debug: bool = False
    threads: int = 1
    updateNames: bool = True

    '''
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir: str = os.path.join(testRoot, 'input/')
    inDirMod: str = os.path.join(testRoot, 'input_mod/')
    outDir: str = os.path.join(testRoot, 'output/')
    outUpd: str = os.path.join(testRoot, 'update/')

    if debug:
        print('Test directory:\t{:s}'.format(testRoot))
        print('Test input dir:\t{:s}'.format(inDir))
        print('Test output dir:\t{:s}'.format(outDir))
        print('Test output dir for update:\t{:s}'.format(outUpd))

    test_remap_pairwise_relations_parallel(debug=debug)
    '''

    return 0


if __name__ == "__main__":
    main()
