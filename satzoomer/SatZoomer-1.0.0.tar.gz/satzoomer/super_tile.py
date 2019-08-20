import socket
from warnings import warn

class Tile:

    ROOT_DIR = r'//ordsvy.gov.uk/Data/BCI_Technical/EOResearch'

    PALETTE = {0: (127, 127, 127), # Buildings (blue)
                1: (255, 255, 255), # Cloud (white)
                2: (255, 0, 255), # Other Surface (green)
                3: (255, 0, 0), # Roads (magenta)
                4: (0, 0, 255), # Sea (yellow)     
                5: (0, 255, 0), # Vegetation (cyan)
                6: (0, 0, 255), # Water
                7: (0, 0, 0)} # Other (black)

    def __init__(self, country):
        self.country = country
        self.ROOT_DIR = Tile.ROOT_DIR
        self.palette = Tile.PALETTE
        self.mask_root = self._get_mask_root()

    def _get_mask_root(self):
        if socket.gethostname() == 'ND30187':
            MASK_ROOT = r'O:\LandCover'
        else:
            warn('This might not work on anything other than ND30187')
            MASK_ROOT = r'//afahpoc1w006/Mask_RCNN/LandCover'
        return MASK_ROOT

    def invert_palette(self):
        invert_palette = {v: k for k, v in self.palette.items()}
        return invert_palette

    
