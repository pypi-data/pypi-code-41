'''
#
# PROTEIN
#
'''

'''
CODING TRANSFORMATION
http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/
'''

from .AminoAcids import AminoAcids
from .Element import PeriodicTable

aminoacids3to1 = {
    'ALA': 'A', 'AZT': 'A', 'CHA': 'A', 'HPH': 'A', 'NAL': 'A', 'AIB': 'A', 'BAL': 'A',
    'DHA': 'A', 'BB9': 'A', 'ALM': 'A', 'AYA': 'A', 'BNN': 'A', 'CHG': 'A', 'CSD': 'A',
    'DAL': 'A', 'DNP': 'A', 'FLA': 'A', 'HAC': 'A', 'MAA': 'A', 'PRR': 'A', 'TIH': 'A',
    'TPQ': 'A', 'BB9': 'A',
    'ARG': 'R', 'ORN': 'R', 'ACL': 'R', 'ARM': 'R', 'AGM': 'R', 'HAR': 'R', 'HMR': 'R',
    'DAR': 'R',
    'ASN': 'N', 'MEN': 'N',
    'ASP': 'D', 'ASZ': 'D', '2AS': 'D', 'ASA': 'D', 'ASB': 'D', 'ASK': 'D', 'ASL': 'D',
    'ASQ': 'D', 'BHD': 'D', 'DAS': 'D', 'DSP': 'D',
    'ASX': 'B',
    'CYS': 'C', 'CYD': 'C', 'CYO': 'C', 'HCY': 'C', 'CSX': 'C', 'SMC': 'C', 'BCS': 'C',
    'BUC': 'C', 'C5C': 'C', 'C6C': 'C', 'CCS': 'C', 'CEA': 'C', 'CME': 'C', 'CSO': 'C',
    'CSP': 'C', 'CSS': 'C', 'CSW': 'C', 'CY1': 'C', 'CY3': 'C', 'CYG': 'C', 'CYM': 'C',
    'CYQ': 'C', 'DCY': 'C', 'OCS': 'C', 'SOC': 'C', 'EFC': 'C', 'PR3': 'C', 'SCH': 'C',
    'SCS': 'C', 'SCY': 'C', 'SHC': 'C', 'PEC': 'C',
    'GLN': 'Q', 'DGN': 'Q',
    'GLU': 'E', 'GLA': 'E', 'GLZ': 'E', 'PCA': 'E', '5HP': 'E', 'CGU': 'E', 'DGL': 'E',
    'GGL': 'E', 'GMA': 'E',
    'GLX': 'Z',
    'GLY': 'G', 'GL3': 'G', 'GLZ': 'G', 'GSC': 'G', 'SAR': 'G', 'MPQ': 'G', 'NMC': 'G',
    'MSA': 'G', 'DBU': 'G',
    'HIS': 'H', 'HSE': 'H', 'HSD': 'H', 'HI0': 'H', 'HIP': 'H', 'HID': 'H', 'HIE': 'H',
    '3AH': 'H', 'MHS': 'H', 'DHI': 'H', 'HIC': 'H', 'NEP': 'H', 'NEM': 'H',
    'ILE': 'I', 'IIL': 'I', 'DIL': 'I',
    'LEU': 'L', 'NLE': 'L', 'LOV': 'L', 'NLN': 'L', 'NLP': 'L', 'MLE': 'L', 'BUG': 'L',
    'CLE': 'L', 'DLE': 'L', 'MLU': 'L',
    'LYS': 'K', 'LYZ': 'K', 'ALY': 'K', 'TRG': 'K', 'SHR': 'K', 'LYM': 'K', 'LLY': 'K',
    'KCX': 'K', 'LLP': 'K', 'DLY': 'K', 'DM0': 'K',
    'MET': 'M', 'MSE': 'M', 'CXM': 'M', 'FME': 'M', 'OMT': 'M',
    'PHE': 'F', 'DAH': 'F', 'HPQ': 'F', 'DPN': 'F', 'PHI': 'F', 'PHL': 'F',
    'PRO': 'P', 'HYP': 'P', 'DPR': 'P', 'ECQ': 'P', 'POM': 'P', 'H5M': 'P',
    'SER': 'S', 'HSE': 'S', 'STA': 'S', 'SVA': 'S', 'SAC': 'S', 'SEL': 'S', 'SEP': 'S',
    'SET': 'S', 'OAS': 'S', 'DSN': 'S', 'MIS': 'S',
    'THR': 'T', 'PTH': 'T', 'ALO': 'T', 'TPO': 'T', 'BMT': 'T', 'DTH': 'T', 'CTH': 'T',
    'TRP': 'W', 'TPL': 'W', 'TRO': 'W', 'DTR': 'W', 'HTR': 'W', 'LTR': 'W',
    'TYR': 'Y', 'TYQ': 'Y', 'TYS': 'Y', 'TYY': 'Y', 'TYB': 'Y', 'STY': 'Y', 'PTR': 'Y',
    'PAQ': 'Y', 'DTY': 'Y', 'IYR': 'Y', 'GHP': 'Y', 'D3P': 'Y', 'D4P': 'Y', 'OMZ': 'Y',
    'OMY': 'Y',
    'VAL': 'V', 'NVA': 'V', 'DVA': 'V', 'DIV': 'V', 'MVA': 'V',
    'SEC': 'U',
    'PYL': 'O',
    'XLE': 'J',
    'ACE': 'X', '3FG': 'X', 'UNK': 'X'
}

aminoacids1to3 = dict([[v, k] for k, v in aminoacids3to1.items()])
aminoacids1to3['A'] = 'ALA'
aminoacids1to3['N'] = 'ASN'
aminoacids1to3['R'] = 'ARG'
aminoacids1to3['D'] = 'ASP'
aminoacids1to3['C'] = 'CYS'
aminoacids1to3['Q'] = 'GLN'
aminoacids1to3['E'] = 'GLU'
aminoacids1to3['G'] = 'GLY'
aminoacids1to3['H'] = 'HIS'
aminoacids1to3['I'] = 'ILE'
aminoacids1to3['J'] = 'XLE'
aminoacids1to3['L'] = 'LEU'
aminoacids1to3['K'] = 'LYS'
aminoacids1to3['M'] = 'MET'
aminoacids1to3['F'] = 'PHE'
aminoacids1to3['O'] = 'PYL'
aminoacids1to3['P'] = 'PRO'
aminoacids1to3['S'] = 'SER'
aminoacids1to3['T'] = 'THR'
aminoacids1to3['U'] = 'SEC'
aminoacids1to3['W'] = 'TRP'
aminoacids1to3['Y'] = 'TYR'
aminoacids1to3['V'] = 'VAL'

'''
REGULAR AMINOACIDS IDENTIFICATION
'''
aminoacids_main3 = set(['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLX', 'GLY', 'HIS', 'ILE', 'LEU',
                        'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL', 'SEC', 'PYL', 'XLE'])

aminoacids_main1 = set(['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V'])

'''
PROPERTIES
'''
aminoacids_surface = {
    'A': 115, 'C': 149, 'D': 170, 'E': 207, 'F': 230, 'G': 86,  'H': 206,
    'I': 187, 'K': 222, 'L': 192, 'M': 210, 'N': 184, 'P': 140, 'Q': 208,
    'R': 263, 'S': 140, 'T': 164, 'V': 161, 'W': 269, 'Y': 257,
}

aminoacids_polarity_boolean = {
    'A': False, 'C': False, 'D': True,  'E': True,  'F': False, 'G': False, 'H': True,
    'I': False, 'K': True,  'L': False, 'M': False, 'N': True,  'P': False, 'Q': True,
    'R': True,  'S': True,  'T': True,  'V': False, 'W': False, 'Y': True
}

aminoacids_groups = {
    'aromatic'    : set(list('HFYW')),
    'negative'    : set(list('DE')),
    'nonpolar'    : set(list('AVILMFWCPG')),
    'polar'       : set(list('STNQY')),
    'positive'    : set(list('RHK')),
    'special'     : set(list('CUGP'))
}

aminoacids_charged_atoms = {
    'D' : set(['OD1', 'OD2']),
    'E' : set(['OE1', 'OE2']),
    'R' : set(['NH1', 'NH2']),
    'H' : set(['ND1', 'NE1']),
    'K' : set(['NZ']),
}

aminoacids_hbond_acceptors = {
    'N' : ['OD1', 'OD1'],
    'D' : ['OD1', 'OD1', 'OD2', 'OD2'],
    'Q' : ['OE1', 'OE1'],
    'E' : ['OE1', 'OE1', 'OE2', 'OE2'],
    'H' : ['ND1', 'NE1'],
    'S' : ['OG' , 'OG'],
    'T' : ['OG1', 'OG1'],
    'Y' : ['OH']
}

aminoacids_hbond_donors = {
    'R' : ['NE' , 'NH1', 'NH1', 'NH2', 'NH2'],
    'N' : ['ND2', 'ND2'],
    'Q' : ['NE2', 'NE2'],
    'H' : ['ND1', 'NE1'],
    'K' : ['NZ' , 'NZ',  'NZ'],
    'S' : ['OG'],
    'T' : ['OG1'],
    'W' : ['NE1'],
    'Y' : ['OH']
}

'''
#
# DNA/RNA
#
'''

'''
CODING TRANSFORMATION
http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/
'''
nucleic3to1  = {
    'A': 'A', 'DA': 'A', 'ADE': 'A', '+A': 'A',
              '00A': 'A', '12A': 'A', '1MA': 'A', '26A': 'A', '2MA': 'A', '5FA': 'A', '6IA': 'A', '6MA': 'A', '6MC': 'A',
              '6MP': 'A', '6MT': 'A', '6MZ': 'A', '8AN': 'A', 'A23': 'A', 'A2L': 'A', 'A2M': 'A', 'A39': 'A', 'A3P': 'A',
              'A44': 'A', 'A5O': 'A', 'A6A': 'A', 'A9Z': 'A', 'ADI': 'A', 'ADP': 'A', 'AET': 'A', 'AMD': 'A', 'AMO': 'A',
              'AP7': 'A', 'AVC': 'A', 'G3A': 'A', 'LCA': 'A', 'MA6': 'A', 'MAD': 'A', 'MGQ': 'A', 'MIA': 'A', 'MTU': 'A',
              'N79': 'A', 'P5P': 'A', 'PPU': 'A', 'PR5': 'A', 'PU': 'A', 'RIA': 'A', 'SRA': 'A', 'T6A': 'A', 'TBN': 'A',
              'TXD': 'A', 'TXP': 'A', 'V3L': 'A', 'ZAD': 'A', '0AM': 'A', '0AV': 'A', '0SP': 'A', '1AP': 'A', '2AR': 'A',
              '2BU': 'A', '2A': 'A', '3A': 'A', '5AA': 'A', '6HA': 'A', '7A': 'A', '8BA': 'A', 'A34': 'A', 'A35': 'A',
              'A38': 'A', 'A3A': 'A', 'A40': 'A', 'A43': 'A', 'A47': 'A', 'A5L': 'A', 'ABR': 'A', 'ABS': 'A', 'AD2': 'A',
              'AF2': 'A', 'AS': 'A', 'DZM': 'A', 'E': 'A', 'E1X': 'A', 'EA': 'A', 'FA2': 'A', 'MA7': 'A', 'PRN': 'A',
              'R': 'A', 'RMP': 'A', 'S4A': 'A', 'SMP': 'A', 'TCY': 'A', 'TFO': 'A', 'XAD': 'A', 'XAL': 'A', 'XUA': 'A',
              'Y': 'A',
    'C': 'C', 'DC': 'C', 'CYT': 'C', '+C': 'C',
              '10C': 'C', '1SC': 'C', '4OC': 'C', '5IC': 'C', '5MC': 'C', 'A5M': 'C', 'A6C': 'C', 'C25': 'C', 'C2L': 'C',
              'C31': 'C', 'C43': 'C', 'C5L': 'C', 'CBV': 'C', 'CCC': 'C', 'CH': 'C', 'CSF': 'C', 'IC': 'C', 'LC': 'C',
              'M4C': 'C', 'M5M': 'C', 'N5M': 'C', 'OMC': 'C', 'PMT': 'C', 'RPC': 'C', 'S4C': 'C', 'ZBC': 'C', 'ZCY': 'C',
              '0AP': 'C', '0R8': 'C', '1CC': 'C', '1FC': 'C', '47C': 'C', '4PC': 'C', '4PD': 'C', '4PE': 'C', '4SC': 'C',
              '5CM': 'C', '5FC': 'C', '5HC': 'C', '5NC': 'C', '5PC': 'C', '6HC': 'C', 'B7C': 'C', 'C2S': 'C', 'C32': 'C',
              'C34': 'C', 'C36': 'C', 'C37': 'C', 'C38': 'C', 'C42': 'C', 'C45': 'C', 'C46': 'C', 'C49': 'C', 'C4S': 'C',
              'CAR': 'C', 'CB2': 'C', 'CBR': 'C', 'CDW': 'C', 'CFL': 'C', 'CFZ': 'C', 'CMR': 'C', 'CP1': 'C', 'CSL': 'C',
              'CX2': 'C', 'CT': 'C', 'DFC': 'C', 'DNR': 'C', 'DOC': 'C', 'EXC': 'C', 'GCK': 'C', 'I5C': 'C', 'IMC': 'C',
              'MCY': 'C', 'ME6': 'C', 'PVX': 'C', 'SC': 'C', 'TC1': 'C', 'TPC': 'C', 'XCL': 'C', 'XCR': 'C', 'XCT': 'C',
              'XCY': 'C', 'YCO': 'C', 'Z': 'C', 
    'G': 'G', 'DG': 'G', 'GUA': 'G', '+G': 'G',
              '0AD': 'G', '0UH': 'G', '2PR': 'G', '5CG': 'G', '63G': 'G', '63H': 'G', '6HG': 'G', '6OG': 'G', '6PO': 'G',
              '7GU': 'G', '8AG': 'G', '8FG': 'G', '8MG': 'G', '8OG': 'G', 'AFG': 'G', 'BGM': 'G', 'C6G': 'G', 'DCG': 'G',
              'DG': 'G', 'DFG': 'G', 'G8': 'G', 'GI': 'G', 'GP': 'G', 'EFG': 'G', 'EHG': 'G', 'FG': 'G', 'FMG': 'G',
              'FOX': 'G', 'G2S': 'G', 'G31': 'G', 'G32': 'G', 'G33': 'G', 'G36': 'G', 'G38': 'G', 'G42': 'G', 'G47': 'G',
              'G49': 'G', 'GDR': 'G', 'GF2': 'G', 'GFL': 'G', 'GMS': 'G', 'GN7': 'G', 'GS': 'G', 'GSR': 'G', 'GSS': 'G',
              'GX1': 'G', 'HN0': 'G', 'HN1': 'G', 'IGU': 'G', 'LCG': 'G', 'LGP': 'G', 'M1G': 'G', 'MG1': 'G', 'MRG': 'G',
              'OGX': 'G', 'P': 'G', 'PG7': 'G', 'PGN': 'G', 'PPW': 'G', 'S4G': 'G', 'S6G': 'G', 'SG': 'G', 'TGP': 'G',
              'X': 'G', 'XGL': 'G', 'XGR': 'G', 'XGU': 'G', 'XUG': 'G', '102': 'G', '18M': 'G', '1MG': 'G', '23G': 'G',
              '2EG': 'G', '2MG': 'G', '7MG': 'G', 'A6G': 'G', 'CG1': 'G', 'G1G': 'G', 'G25': 'G', 'G2L': 'G', 'G3A': 'G',
              'G46': 'G', 'G48': 'G', 'G7M': 'G', 'GAO': 'G', 'GDO': 'G', 'GDP': 'G', 'GH3': 'G', 'GNG': 'G', 'GOM': 'G',
              'GRB': 'G', 'GTP': 'G', 'IG': 'G', 'IMP': 'G', 'KAG': 'G', 'LG': 'G', 'M2G': 'G', 'MGT': 'G', 'MGV': 'G',
              'N6G': 'G', 'O2G': 'G', 'OMG': 'G', 'PGP': 'G', 'QUO': 'G', 'TPG': 'G', 'XTS': 'G', 'YG': 'G', 'YYG': 'G',
              'ZGU': 'G',
    'I': 'I', 'DI': 'I', 'INO': 'I', '+I': 'I',
              '2BD': 'I', 'OIP': 'I', 
    'T': 'T', 'DT': 'T', 'THY': 'T', '+T': 'T',
              '2AT': 'T', '2BT': 'T', '2T': 'T', '2GT': 'T', '2NT': 'T', '2OT': 'T', '2ST': 'T', '5AT': 'T', '5HT': 'T',
              '5IT': 'T', '5PY': 'T', '64T': 'T', '6CT': 'T', '6HT': 'T', 'ATD': 'T', 'ATL': 'T', 'ATM': 'T', 'BOE': 'T',
              'CTG': 'T', 'D3T': 'T', 'D4M': 'T', 'DPB': 'T', 'DRT': 'T', 'EIT': 'T', 'F3H': 'T', 'F4H': 'T', 'JT': 'T',
              'MMT': 'T', 'MTR': 'T', 'NMS': 'T', 'NMT': 'T', 'P2T': 'T', 'PST': 'T', 'S2M': 'T', 'SPT': 'T', 'T32': 'T',
              'T36': 'T', 'T37': 'T', 'T39': 'T', 'T3P': 'T', 'T48': 'T', 'T49': 'T', 'T4S': 'T', 'T5S': 'T', 'TA3': 'T',
              'TAF': 'T', 'TCP': 'T', 'TDY': 'T', 'TED': 'T', 'TFE': 'T', 'TFF': 'T', 'TFT': 'T', 'TLC': 'T', 'TP1': 'T',
              'TTD': 'T', 'TTM': 'T', 'US3': 'T', 'XTF': 'T', 'XTH': 'T', 'XTL': 'T', 'XTR': 'T', 
    'U': 'U', 'DU': 'U', 'URA': 'U', '+U': 'U',
              '0AU': 'U', '18Q': 'U', '5HU': 'U', '5IU': 'U', '5SE': 'U', 'BRU': 'U', 'BVP': 'U', 'DDN': 'U', 'DRM': 'U',
              'UZ': 'U', 'GMU': 'U', 'HDP': 'U', 'HEU': 'U', 'NDN': 'U', 'NU': 'U', 'OHU': 'U', 'P2U': 'U', 'PU': 'U',
              'T5O': 'U', 'TLN': 'U', 'TTI': 'U', 'U2N': 'U', 'U33': 'U', 'UBI': 'U', 'UBR': 'U', 'UCL': 'U', 'UF2': 'U',
              'UFR': 'U', 'UFT': 'U', 'UMS': 'U', 'UMX': 'U', 'UPE': 'U', 'UPS': 'U', 'URX': 'U', 'US1': 'U', 'US2': 'U',
              'USM': 'U', 'UVX': 'U', 'ZU': 'U', '125': 'U', '126': 'U', '127': 'U', '1RN': 'U', '2AU': 'U', '2MU': 'U',
              '2OM': 'U', '3AU': 'U', '3ME': 'U', '3MU': 'U', '3TD': 'U', '4SU': 'U', '5BU': 'U', '5FU': 'U', '5MU': 'U',
              '70U': 'U', 'A6U': 'U', 'CNU': 'U', 'DHU': 'U', 'FHU': 'U', 'FNU': 'U', 'H2U': 'U', 'IU': 'U', 'LHU': 'U',
              'MEP': 'U', 'MNU': 'U', 'OMU': 'U', 'ONE': 'U', 'PSU': 'U', 'PYO': 'U', 'RSQ': 'U', 'RUS': 'U', 'S4U': 'U',
              'SSU': 'U', 'SUR': 'U', 'T31': 'U', 'U25': 'U', 'U2L': 'U', 'U2P': 'U', 'U31': 'U', 'U34': 'U', 'U36': 'U',
              'U37': 'U', 'U8U': 'U', 'UAR': 'U', 'UBB': 'U', 'UBD': 'U', 'UD5': 'U', 'UPV': 'U', 'UR3': 'U', 'URD': 'U',
              'US5': 'U', 'UZR': 'U', 'ZBU': 'U'
}

nucleic1to3 = dict([[v,k] for k,v in nucleic3to1.items()])
nucleic1to3['A'] = 'DA'
nucleic1to3['C'] = 'DC'
nucleic1to3['G'] = 'DG'
nucleic1to3['I'] = 'DI'
nucleic1to3['T'] = 'DT'
nucleic1to3['U'] = 'DU'

'''
REGULAR NUCLEOTIDES IDENTIFICATION
'''
nucleic_main3 = set(['ADE', 'CYT', 'GUA', 'INO', 'THY', 'URA'])

nucleic_main2 = set(['DA', 'DC', 'DG', 'DI', 'DT', 'DU'])

nucleic_main1 = set(['A', 'C', 'G', 'I', 'T', 'U'])

'''
PROPERTIES
'''
nitrogenous_bases = {
    'A': 'U', 'C': 'Y', 'G': 'U', 'I': 'U', 'T': 'Y', 'U': 'Y'
}

dna_complementary = {
    'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A', 'I': 'C', 'N': 'N',
    'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'u': 'a', 'i': 'c', 'n': 'n',
}

rna_complementary = {
    'A': 'U', 'C': 'G', 'G': 'C', 'U': 'A', 'T': 'A', 'I': 'C', 'N': 'N',
    'a': 'u', 'c': 'g', 'g': 'c', 'u': 'a', 't': 'a', 'i': 'c', 'n': 'n',
}

nucleotides_hbond_acceptors = {
    'A' : ['N3', 'N7'],
    'C' : ['O2'],
    'G' : ['N3', 'N7', 'O6'],
    'T' : ['O2', 'O4'],
}

# According to definition by Mandel-Gutfreund Y., Margalit H., Jernigan J.L.
# & Zhurkin V.B., 1998, a C-hydrogen bond is formed by a CH-O pair at 3.5A.
# Specifically between the C5 of Cytosine and the C5M of Thymine and an O.
nucleotides_hbond_donors = {
    'A' : ['N6'],
    'C' : ['C5', 'N4'],
    'G' : ['N2'],
    'T' : ['C5M'],
}

'''
CRYSTALOGRAPHIC METHODS
'''
crystal_method_has_resolution = set(['X-RAY DIFFRACTION', 'ELECTRON MICROSCOPY', 'NEUTRON DIFFRACTION',
                                     'FIBER DIFFRACTION', 'ELECTRON CRYSTALLOGRAPHY'])

crystal_method_not_resolution = set(['SOLUTION NMR', 'POWDER DIFFRACTION', 'SOLUTION SCATTERING', 'SOLID-STATE NMR',
                                     'INFRARED SPECTROSCOPY', 'FLUORESCENCE TRANSFER'])

crystal_method                = crystal_method_has_resolution.union(crystal_method_not_resolution)


# '''
# Elements
# '''


# class Element(object):
#     def __init__(self, number, symbol, name):
#         self.number = number
#         self.symbol = symbol
#         self.name   = name

# element_dic = {
#     'H':  Element(  1, 'H',  'Hydrogen'),    'He': Element(  2, 'He', 'Helium'),
#     'Li': Element(  3, 'Li', 'Lithium'),     'Be': Element(  4, 'Be', 'Beryllium'),
#     'B':  Element(  5, 'B',  'Boron'),       'C':  Element(  6, 'C',  'Carbon'),
#     'N':  Element(  7, 'N',  'Nitrogen'),    'O':  Element(  8, 'O',  'Oxygen'),
#     'F':  Element(  9, 'F',  'Fluorine'),    'Ne': Element( 10, 'Ne', 'Neon'),
#     'Na': Element( 11, 'Na', 'Sodium'),      'Mg': Element( 12, 'Mg', 'Magnesium'),
#     'Al': Element( 13, 'Al', 'Aluminium'),   'Si': Element( 14, 'Si', 'Silicon'),
#     'P':  Element( 15, 'P',  'Phosphorus'),  'S':  Element( 16, 'S',  'Sulfur'),
#     'Cl': Element( 17, 'Cl', 'Chlorine'),    'Ar': Element( 18, 'Ar', 'Argon'),
#     'K':  Element( 19, 'K',  'Potassium'),   'Ca': Element( 20, 'Ca', 'Calcium'),
#     'Sc': Element( 21, 'Sc', 'Scandium'),    'Ti': Element( 22, 'Ti', 'Titanium'),
#     'V':  Element( 23, 'V',  'Vanadium'),    'Cr': Element( 24, 'Cr', 'Chromium'),
#     'Mn': Element( 25, 'Mn', 'Manganese'),   'Fe': Element( 26, 'Fe', 'Iron'),
#     'Co': Element( 27, 'Co', 'Cobalt'),      'Ni': Element( 28, 'Ni', 'Nickel'),
#     'Cu': Element( 29, 'Cu', 'Copper'),      'Zn': Element( 30, 'Zn', 'Zinc'),
#     'Ga': Element( 31, 'Ga', 'Gallium'),     'Ge': Element( 32, 'Ge', 'Germanium'),
#     'As': Element( 33, 'As', 'Arsenic'),     'Se': Element( 34, 'Se', 'Selenium'),
#     'Br': Element( 35, 'Br', 'Bromine'),     'Kr': Element( 36, 'Kr', 'Krypton'),
#     'Rb': Element( 37, 'Rb', 'Rubidium'),    'Sr': Element( 38, 'Sr', 'Strontium'),
#     'Y':  Element( 39, 'Y',  'Yttrium'),     'Zr': Element( 40, 'Zr', 'Zirconium'),
#     'Nb': Element( 41, 'Nb', 'Niobium'),     'Mo': Element( 42, 'Mo', 'Molybdenum'),
#     'Tc': Element( 43, 'Tc', 'Technetium'),  'Ru': Element( 44, 'Ru', 'Ruthenium'),
#     'Rh': Element( 45, 'Rh', 'Rhodium'),     'Pd': Element( 46, 'Pd', 'Palladium'),
#     'Ag': Element( 47, 'Ag', 'Silver'),      'Cd': Element( 48, 'Cd', 'Cadmium'),
#     'In': Element( 49, 'In', 'Indium'),      'Sn': Element( 50, 'Sn', 'Tin'),
#     'Sb': Element( 51, 'Sb', 'Antimony'),    'Te': Element( 52, 'Te', 'Tellurium'),
#     'I':  Element( 53, 'I',  'Iodine'),      'Xe': Element( 54, 'Xe', 'Xenon'),
#     'Cs': Element( 55, 'Cs', 'Caesium'),     'Ba': Element( 56, 'Ba', 'Barium'),
#     'La': Element( 57, 'La', 'Lanthanum'),   'Ce': Element( 58, 'Ce', 'Cerium'),
#     'Pr': Element( 59, 'Pr', 'Praseodymium'), 'Nd': Element( 60, 'Nd', 'Neodymium'),
#     'Pm': Element( 61, 'Pm', 'Promethium'),  'Sm': Element( 62, 'Sm', 'Samarium'),
#     'Eu': Element( 63, 'Eu', 'Europium'),    'Gd': Element( 64, 'Gd', 'Gadolinium'),
#     'Tb': Element( 65, 'Tb', 'Terbium'),     'Dy': Element( 66, 'Dy', 'Dysprosium'),
#     'Ho': Element( 67, 'Ho', 'Holmium'),     'Er': Element( 68, 'Er', 'Erbium'),
#     'Tm': Element( 69, 'Tm', 'Thulium'),     'Yb': Element( 70, 'Yb', 'Ytterbium'),
#     'Lu': Element( 71, 'Lu', 'Lutetium'),    'Hf': Element( 72, 'Hf', 'Hafnium'),
#     'Ta': Element( 73, 'Ta', 'Tantalum'),    'W':  Element( 74, 'W', 'Tungsten'),
#     'Re': Element( 75, 'Re', 'Rhenium'),     'Os': Element( 76, 'Os', 'Osmium'),
#     'Ir': Element( 77, 'Ir', 'Iridium'),     'Pt': Element( 78, 'Pt', 'Platinum'),
#     'Au': Element( 79, 'Au', 'Gold'),        'Hg': Element( 80, 'Hg', 'Mercury'),
#     'Tl': Element( 81, 'Tl', 'Thallium'),    'Pb': Element( 82, 'Pb', 'Lead'),
#     'Bi': Element( 83, 'Bi', 'Bismuth'),     'Po': Element( 84, 'Po', 'Polonium'),
#     'At': Element( 85, 'At', 'Astatine'),    'Rn': Element( 86, 'Rn', 'Radon'),
#     'Fr': Element( 87, 'Fr', 'Francium'),    'Ra': Element( 88, 'Ra', 'Radium'),
#     'Ac': Element( 89, 'Ac', 'Actinium'),    'Th': Element( 90, 'Th', 'Thorium'),
#     'Pa': Element( 91, 'Pa', 'Protactinium'), 'U':  Element( 92, 'U', 'Uranium'),
#     'Np': Element( 93, 'Np', 'Neptunium'),   'Pu': Element( 94, 'Pu', 'Plutonium'),
#     'Am': Element( 95, 'Am', 'Americium'),   'Cm': Element( 96, 'Cm', 'Curium'),
#     'Bk': Element( 97, 'Bk', 'Berkelium'),   'Cf': Element( 98, 'Cf', 'Californium'),
#     'Es': Element( 99, 'Es', 'Einsteinium'), 'Fm': Element(100, 'Fm', 'Fermium'),
#     'Md': Element(101, 'Md', 'Mendelevium'), 'No': Element(102, 'No', 'Nobelium'),
#     'Lr': Element(103, 'Lr', 'Lawrencium'),  'Rf': Element(104, 'Rf', 'Rutherfordium'),
#     'Db': Element(105, 'Db', 'Dubnium'),     'Sg': Element(106, 'Sg', 'Seaborgium'),
#     'Bh': Element(107, 'Bh', 'Bohrium'),     'Hs': Element(108, 'Hs', 'Hassium'),
#     'Mt': Element(109, 'Mt', 'Meitnerium'),  'Ds': Element(110, 'Ds', 'Darmstadtium'),
#     'Rg': Element(111, 'Rg', 'Roentgenium'), 'Cn': Element(112, 'Cn', 'Copernicium')
# }