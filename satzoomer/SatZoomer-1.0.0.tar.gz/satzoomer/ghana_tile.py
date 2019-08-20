from super_tile import Tile
import os 
from skimage.io import imread, imsave
from spectral_indices import ndvi, ndwi, bare_soil_index

class GhanaTile(Tile):

    STRIDE = 64
    SIZE = 256

    def __init__(self, tile_number):
        super().__init__('Ghana')
        self.tile_number = tile_number
        self.rgb_dir = self._get_imagery_dir('rgb')
        self.irg_dir = self._get_imagery_dir('irg')
        self.mask_dir = self._get_mask_dir()
        self.classes = self._get_classes()
        self.stride, self.size = GhanaTile.STRIDE, GhanaTile.SIZE

    def __repr__(self):
        return repr(f'{self.tile_number} in Ghana')
 
    def _get_imagery_dir(self, bands):
        return os.path.join(self.ROOT_DIR, 'Ghana', 'Techiman', f'{bands.upper()}')        

    def _get_mask_dir(self):
        return os.path.join(self.mask_root, f'guyana_{str(GhanaTile.STRIDE)}_all_layers', f'{self.tile_number}', 'Masks')

    def _get_classes(self):
        os.chdir(self.mask_dir)
        classes = [d.split('_')[0] for d in os.listdir('.') if os.path.isdir(d)]
        return classes 

    def get_image(self, bands, crop_to_size=False):
        if bands == 'irg':
            img_dir = self.irg_dir
        elif bands == 'rgb':
            img_dir = self.rgb_dir
        else:
            raise Exception('Only looking for irg / rgb ')

        img_path = os.path.join(img_dir, f'{self.tile_number}.tif')
        img = imread(img_path)
        if crop_to_size:
            img = img[:9 * self.size, :9 * self.size, :]
        return img

    def get_heatmap(self, class_, crop_to_size=False):
        heatmap_path = os.path.join(self.mask_dir, f'{class_}_masks', f'{self.tile_number}_heatmap.tif')
        heatmap = imread(heatmap_path)
        if crop_to_size:
            padding = self.size - 2 * self.stride
            heatmap = heatmap[padding: padding + 9 * self.size, padding: padding + 9 * self.size]
        return heatmap

    def save_all_dl_heatmaps(self, outdir, crop_to_size=False):
        classes = self.classes
        for class_ in classes:
            hm = self.get_heatmap(class_, crop_to_size=crop_to_size)
            imsave(os.path.join(outdir, f'{self.tile_number}_{class_}.tif'), hm)

    def spectral_index(self, index, threshold=True, crop_to_size=False):       
        if index == 'ndvi':
            img = self.get_image(bands='irg', crop_to_size=crop_to_size)
            out_image = ndvi(img, threshold=threshold)
        elif index == 'ndwi':
            img = self.get_image(bands='irg', crop_to_size=crop_to_size)
            out_image = ndwi(img)
        elif index == 'bi':
            img = self.get_image(bands='rgb', crop_to_size=crop_to_size)
            out_image = bare_soil_index(img)
        return out_image

    def make_landcover_map(self):
        """
        1a. Get Vegetation Heatmap from NDVI
        1b. Take average with Vegetation Heatmap from DL
        2. Get Buildings from DL
        3. Get OtherSurface from DL
        4. Get Roads from DL
        5. Get Water from NDWI (will need fixing)
        6. Take argmax for each pixel ('unclassifiable' if all classes are 0)
        """
        pass


 
def main():
    tile_number = 'TM0032'
    tile = GhanaTile(tile_number)
    print(repr(tile))
    mask_dir = tile.mask_dir
    print(mask_dir)
    classes = tile.classes
    print(classes)
    rgb = tile.get_image(bands='rgb', crop_to_size=True)
    out_dir = r"C:\Users\JRainbow\Documents\Python Scripts\RulesBasedClassification\images"
    # for class_ in classes:
    #     hm = tile.get_heatmap(class_, crop_to_size=True)
    #     imsave(os.path.join(out_dir, f'{tile_number}_{class_}_crop.tif'), hm)    
    # imsave(os.path.join(out_dir, f'{tile_number}_rgb_crop.tif'), rgb)
    # ndvi = tile.spectral_index(index='ndvi', threshold=True, crop_to_size=True)
    ndwi = tile.spectral_index(index='ndwi', threshold=0.5, crop_to_size=True)
    bi = tile.spectral_index(index='bi', crop_to_size=True)
    # imsave(os.path.join(out_dir, f'{tile_number}_ndvi_thresh.tif'), ndvi)
    imsave(os.path.join(out_dir, f'{tile_number}_bi.tif'), bi)



if __name__ == '__main__':
    main()
