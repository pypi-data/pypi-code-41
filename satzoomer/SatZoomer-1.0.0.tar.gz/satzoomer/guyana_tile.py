from super_tile import Tile
from spectral_indices import ndvi, ndwi

class GuyanaTile(Tile):

    def __init__(self, tile_number):
        super().__init__('Guyana')
        self.tile_number = tile_number

    def __repr__(self):
        return repr(f'{self.tile_number} in Guyana')

    def _get_imagery_dir(self, bands):
        # os.path.join(self.ROOT_DIR, )
        pass
        

    def _get_mask_dir(self):
 
def main():
    tile_number = 'GT0014'
    tile = GuyanaTile(tile_number)
    print(repr(tile))

if __name__ == '__main__':
    main()
