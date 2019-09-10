# data helper code

# DataCollector

import os
import PIL
from PIL import Image
import numpy as np

jzazbz_map = np.load('./jzazbz_array.npy', encoding = 'latin1')

def rgb_to_jzazbz(rgb_array):
    jzazbz_array = np.zeros(rgb_array.shape)
    for i in range(rgb_array.shape[0]):
        for j in range(rgb_array.shape[1]):
            jzazbz_array[i][j] = jzazbz_map[rgb_array[i][j][0]][rgb_array[i][j][1]][rgb_array[i][j][2]]
    return jzazbz_array

class ImageDict():
    def __init__(self, **kwargs):
        self.rgb = {}
        self.jzazbz = {}


    def load_images_from_subfolders(self, path):
        assert os.path.isdir(path)
        path = os.path.realpath(path)
        folders = os.listdir(path)
        for folder in folders:
            fp = os.path.join(path, folder)
            assert os.path.isdir(fp)
            self.load_images_from_folder(fp)

    def load_images_from_folder(self, path, label=None):
        assert os.path.isdir(path)
        path = os.path.realpath(path)
        label = label or path.split('/')[-1]
        files = os.listdir(path)
        imglist = []
        arraylist = []
        for file in files:
            fp = os.path.join(path, file)
            img = None
            try:
                img = self.load_RGB_image(fp)
            except:
                pass
            if img:
                imglist.append(np.array(img))
        self.rgb[label] = imglist

    def load_RGB_image(self, path, compress_dim=300):
        fmts = ['.jpg', '.jpeg', '.png', '.bmp']
        if os.path.isfile(path) and any([fmt in path.lower() for fmt in fmts]):
            try:
                img_raw = PIL.Image.open(path)
                if compress_dim:
                    img_raw = img_raw.resize((compress_dim,compress_dim),
                                                PIL.Image.ANTIALIAS)
                return img_raw
            except:
                pass

    def get_jzazbz_from_rgb(self, label=None):
        if label and label in self.rgb.keys():
            self.jzazbz[label] = [rgb_to_jzazbz(rgb) for rgb in self.rgb[label]]
        else:
            for label in self.rgb.keys():
                self.jzazbz[label] = [rgb_to_jzazbz(rgb) for rgb in self.rgb[label]]

    def print_labels(self):
        assert set(self.rgb.keys()) == set(self.jzazbz.keys())
        print(self.rgb.keys())


#class ImageDownload(self):
    #build_image(input_string)
    #build_request(image, annotation = ['label', 'web'])
    #get_annotations(request)
    #chunks(l, n)
    #divide_chunks(l, n)
    #run_google_vision(myImageList)
    #write_to_json(to_save, filename)
    #download_images(keywords, n)
    #filter_imgs_w_google_scoring(img_json, DLpath, top_n)
    #get_filtered_img_set(filtered_dict, home)
    #get_imgs(searchterms_list, home)
    #get_responses(keywords, n, path, filename, use_filter=False)
