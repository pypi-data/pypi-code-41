"""
Mask R-CNN
Common utility functions and classes.

Copyright (c) 2017 Matterport, Inc.
Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla

Copyright (c) 2019 Infolab.
Licensed under the MIT License (see LICENSE for details)
Written by Donggun LEE
"""

import json
import random
import numpy as np
import skimage.color
import skimage.io
import skimage.transform
from PIL import Image as pImage, ImageDraw, ImageFont
from distutils.version import LooseVersion

from . import Config
from deepgeo.image import obj as Image

class SupportFormatError(Exception):
    def _init_(self, format_):
        self.value = "SupportFormatError: Format '"+format_+"' is not supported."
    
    def _str_(self):
        return self.value  

class Dataset:
    def __init__(self, class_map=None):
        self._image_ids = []
        self.image_info = []
        # Background is always the first class
        self.class_info = [{"source": "", "id": 0, "name": "BG"}]
        self.source_class_ids = {}

    def add_class(self, source, class_id, class_name):
        assert "." not in source, "Source name cannot contain a dot"
        # Does the class exist already?
        for info in self.class_info:
            if info['source'] == source and info["id"] == class_id:
                # source.class_id combination already available, skip
                return
        # Add the class
        self.class_info.append({
            "source": source,
            "id": class_id,
            "name": class_name,
        })

    def add_image(self, source, image_id, path, **kwargs):
        image_info = {
            "id": image_id,
            "source": source,
            "path": path,
        }
        image_info.update(kwargs)
        self.image_info.append(image_info)

    def set_config(self, config:Config):
        """
           # set_config : 설정 데이터를 셋팅합니다.
           
            config : 설정할 Config 데이터를 받습니다.
        """
        self._config_ = config 
        category = self._config_.CATEGORY[1:]
        for idx in range(1, len(category) + 1):
            self.add_class("deepGeo", idx, category[idx - 1])
        del category

    def add_data(self, data):
        """
            # add_data : 학습하거나 검증할 데이터를 넣습니다.

            data : json 파일명이나 list, stphoto, Image 데이터를 넣을 수 있습니다.
        """
        if isinstance(data, str) is True:
            if data.split(".")[-1] == 'json':
                uri = data
                data=None
                with open(uri) as data_file:    
                    data = json.load(data_file)
            else:
                data = json.loads(data)
        if isinstance(data, list) is True:
            for item in data:
                self.add_data(item)
        elif isinstance(data,dict):
            self._add_data_(Image(data['uri'],self._config_.IMAGE_PATH,data['annotations']))
        elif isinstance(data,Image):
            self._add_data_(data)
        else:
            raise SupportFormatError(type(data))

    def _add_data_(self, data:Image):
        """
            # _add_data_ : Image 데이터를 넣습니다.

            data : Image 타입을 받습니다. 
        """
        if isinstance(data, Image):
            self.add_image("deepGeo", image_id=len(self.image_info), path=data.get_path() + data.get_file_name(), image = data.to_stphoto())
            categories = self._config_.CATEGORY
            annotations = data.get_annotation()
            for annotation in annotations:
                if 'annotationText' in annotation:
                    text = annotation['annotationText']
                    if not(text in categories):
                        self.add_class("deepGeo", len(categories), text)
                        categories.append(text)
            self._config_.set_config("CATEGORY",categories)
        else:
            raise SupportFormatError(type(data))
    
    def load_mask(self, image_id):
        """
            # load_mask : Mask R-CNN에서 학습할 때 사용하는 Interface 함수 입니다.
        """
        info = self.image_info[image_id]
        image = info['image']
        annotations = image['annotations']
        width = image['width']
        height = image['height']
        mask = np.zeros([height, width, len(annotations)],dtype=np.uint8)
        class_ids = []
        idx=0
        for annotation in annotations:
            if 'areaInImage' in list(annotation.keys()):
                if 'annotationText' in list(annotation.keys()):
                    polygon = pImage.new('L',(width, height), 0)
                    area = annotation['areaInImage']
                    coordinates = area['coordinates']
                    if area['type'] in ['Rectangle', 'mbr']:
                        ImageDraw.Draw(polygon).rectangle(coordinates, fill=1)
                    elif area['type'] == 'Polygon':
                        if isinstance(coordinates[0], list)==False:
                            coordinates = [coordinates]
                        if len(coordinates[0])==2:
                            coordinates = [sum(coordinates, [])]
                        for coordinate in coordinates:
                            ImageDraw.Draw(polygon).polygon(coordinate, fill=1)
                    mask_ = np.array(polygon)
                    for i in range(height):
                        for j in range(width):
                            mask[i][j][idx]=mask_[i][j]
                    idx+=1
                    class_ids.append(self._config_.CATEGORY.index(annotation['annotationText']))
                    del mask_
                    del area
                    del coordinates
                    del polygon
        del width
        del height
        del annotations
        del info
        del image
        return mask, np.array(class_ids)

    def image_reference(self, image_id):
        """
            # image_reference : Mask R-CNN에서 학습할 때 사용하는 Interface 함수 입니다.
        """
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "deepGeo":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

    def prepare(self, class_map=None):
        """Prepares the Dataset class for use.

        TODO: class map is not supported yet. When done, it should handle mapping
              classes from different datasets to the same class ID.
        """

        def clean_name(name):
            """Returns a shorter version of object names for cleaner display."""
            return ",".join(name.split(",")[:1])

        # Build (or rebuild) everything else from the info dicts.
        self.num_classes = len(self.class_info)
        self.class_ids = np.arange(self.num_classes)
        self.class_names = [clean_name(c["name"]) for c in self.class_info]
        self.num_images = len(self.image_info)
        self._image_ids = np.arange(self.num_images)

        # Mapping from source class and image IDs to internal IDs
        self.class_from_source_map = {"{}.{}".format(info['source'], info['id']): id
                                      for info, id in zip(self.class_info, self.class_ids)}
        self.image_from_source_map = {"{}.{}".format(info['source'], info['id']): id
                                      for info, id in zip(self.image_info, self.image_ids)}

        # Map sources to class_ids they support
        self.sources = list(set([i['source'] for i in self.class_info]))
        self.source_class_ids = {}
        # Loop over datasets
        for source in self.sources:
            self.source_class_ids[source] = []
            # Find classes that belong to this dataset
            for i, info in enumerate(self.class_info):
                # Include BG class in all datasets
                if i == 0 or source == info['source']:
                    self.source_class_ids[source].append(i)

    def map_source_class_id(self, source_class_id):
        """Takes a source class ID and returns the int class ID assigned to it.

        For example:
        dataset.map_source_class_id("coco.12") -> 23
        """
        return self.class_from_source_map[source_class_id]
    
    def get_source_class_id(self, class_id, source):
        """Map an internal class ID to the corresponding class ID in the source dataset."""
        info = self.class_info[class_id]
        assert info['source'] == source
        return info['id']
    
    @property
    def image_ids(self):
        return self._image_ids

    def source_image_link(self, image_id):
        """Returns the path or URL to the image.
        Override this to return a URL to the image if it's available online for easy
        debugging.
        """
        return self.image_info[image_id]["path"]

    def load_image(self, image_id):
        """Load the specified image and return a [H,W,3] Numpy array.
        """
        # Load image
        image = skimage.io.imread(self.image_info[image_id]['path'])
        # If grayscale. Convert to RGB for consistency.
        if image.ndim != 3:
            image = skimage.color.gray2rgb(image)
        # If has an alpha channel, remove it for consistency
        if image.shape[-1] == 4:
            image = image[..., :3]
        return image

def resize_image(image, min_dim=None, max_dim=None, min_scale=None, mode="square"):
    """Resizes an image keeping the aspect ratio unchanged.

    min_dim: if provided, resizes the image such that it's smaller
        dimension == min_dim
    max_dim: if provided, ensures that the image longest side doesn't
        exceed this value.
    min_scale: if provided, ensure that the image is scaled up by at least
        this percent even if min_dim doesn't require it.
    mode: Resizing mode.
        none: No resizing. Return the image unchanged.
        square: Resize and pad with zeros to get a square image
            of size [max_dim, max_dim].
        pad64: Pads width and height with zeros to make them multiples of 64.
               If min_dim or min_scale are provided, it scales the image up
               before padding. max_dim is ignored in this mode.
               The multiple of 64 is needed to ensure smooth scaling of feature
               maps up and down the 6 levels of the FPN pyramid (2**6=64).
        crop: Picks random crops from the image. First, scales the image based
              on min_dim and min_scale, then picks a random crop of
              size min_dim x min_dim. Can be used in training only.
              max_dim is not used in this mode.

    Returns:
    image: the resized image
    window: (y1, x1, y2, x2). If max_dim is provided, padding might
        be inserted in the returned image. If so, this window is the
        coordinates of the image part of the full image (excluding
        the padding). The x2, y2 pixels are not included.
    scale: The scale factor used to resize the image
    padding: Padding added to the image [(top, bottom), (left, right), (0, 0)]
    """
    # Keep track of image dtype and return results in the same dtype
    image_dtype = image.dtype
    # Default window (y1, x1, y2, x2) and default scale == 1.
    h, w = image.shape[:2]
    window = (0, 0, h, w)
    scale = 1
    padding = [(0, 0), (0, 0), (0, 0)]
    crop = None

    if mode == "none":
        return image, window, scale, padding, crop

    # Scale?
    if min_dim:
        # Scale up but not down
        scale = max(1, min_dim / min(h, w))
    if min_scale and scale < min_scale:
        scale = min_scale

    # Does it exceed max dim?
    if max_dim and mode == "square":
        image_max = max(h, w)
        if round(image_max * scale) > max_dim:
            scale = max_dim / image_max

    # Resize image using bilinear interpolation
    if scale != 1:
        image = resize(image, (round(h * scale), round(w * scale)),
                       preserve_range=True)

    # Need padding or cropping?
    if mode == "square":
        # Get new height and width
        h, w = image.shape[:2]
        top_pad = (max_dim - h) // 2
        bottom_pad = max_dim - h - top_pad
        left_pad = (max_dim - w) // 2
        right_pad = max_dim - w - left_pad
        padding = [(top_pad, bottom_pad), (left_pad, right_pad), (0, 0)]
        image = np.pad(image, padding, mode='constant', constant_values=0)
        window = (top_pad, left_pad, h + top_pad, w + left_pad)
    elif mode == "pad64":
        h, w = image.shape[:2]
        # Both sides must be divisible by 64
        assert min_dim % 64 == 0, "Minimum dimension must be a multiple of 64"
        # Height
        if h % 64 > 0:
            max_h = h - (h % 64) + 64
            top_pad = (max_h - h) // 2
            bottom_pad = max_h - h - top_pad
        else:
            top_pad = bottom_pad = 0
        # Width
        if w % 64 > 0:
            max_w = w - (w % 64) + 64
            left_pad = (max_w - w) // 2
            right_pad = max_w - w - left_pad
        else:
            left_pad = right_pad = 0
        padding = [(top_pad, bottom_pad), (left_pad, right_pad), (0, 0)]
        image = np.pad(image, padding, mode='constant', constant_values=0)
        window = (top_pad, left_pad, h + top_pad, w + left_pad)
    elif mode == "crop":
        # Pick a random crop
        h, w = image.shape[:2]
        y = random.randint(0, (h - min_dim))
        x = random.randint(0, (w - min_dim))
        crop = (y, x, min_dim, min_dim)
        image = image[y:y + min_dim, x:x + min_dim]
        window = (0, 0, min_dim, min_dim)
    else:
        raise Exception("Mode {} not supported".format(mode))
    return image.astype(image_dtype), window, scale, padding, crop

def resize(image, output_shape, order=1, mode='constant', cval=0, clip=True,
           preserve_range=False, anti_aliasing=False, anti_aliasing_sigma=None):
    """A wrapper for Scikit-Image resize().

    Scikit-Image generates warnings on every call to resize() if it doesn't
    receive the right parameters. The right parameters depend on the version
    of skimage. This solves the problem by using different parameters per
    version. And it provides a central place to control resizing defaults.
    """
    if LooseVersion(skimage.__version__) >= LooseVersion("0.14"):
        # New in 0.14: anti_aliasing. Default it to False for backward
        # compatibility with skimage 0.13.
        return skimage.transform.resize(
            image, output_shape,
            order=order, mode=mode, cval=cval, clip=clip,
            preserve_range=preserve_range, anti_aliasing=anti_aliasing,
            anti_aliasing_sigma=anti_aliasing_sigma)
    else:
        return skimage.transform.resize(
            image, output_shape,
            order=order, mode=mode, cval=cval, clip=clip,
            preserve_range=preserve_range)
