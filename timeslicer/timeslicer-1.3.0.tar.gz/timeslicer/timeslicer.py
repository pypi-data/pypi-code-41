import math
import os
import os.path
import random

from PIL import Image


def timeslice(image_folder: str, output_path: str, skip=1, reverse=False, randomize=False, qual=95):
    try:
        num_photos = math.floor(len([im for im in os.listdir(image_folder)]) / skip)
    except FileNotFoundError:
        raise FileNotFoundError

    if num_photos < skip:
        print("skip > number of photos")
        raise ValueError

    try:
        slice_width, image_height = Image.open(image_folder + os.listdir(image_folder)[0]).size
        slice_width = math.floor(slice_width / num_photos)
    except (FileNotFoundError, OSError) as err:
        raise err

    def image_gen(skip):
        c = 0
        for photo in sorted([Image.open(image_folder + im) for im in os.listdir(image_folder)],
                            key=lambda x: x.filename, reverse=reverse):
            if c % skip == 0:
                yield photo
            c += 1

    photo_list = image_gen(skip) 
    slices = [None]*num_photos

    if not randomize:
        for i in range(num_photos):
            im = photo_list.__next__()
            left = i * slice_width
            right = left + slice_width
            sliced = im.crop((left, 0, right, image_height))
            slices[i] = sliced
    else:
        l = [x for x in range(num_photos)]
        random.shuffle(l)
        for i in l:
            im = photo_list.__next__()
            left = i * slice_width
            right = left + slice_width
            sliced = im.crop((left, 0, right, image_height))
            slices[i] = sliced

    result_width = slice_width * len(slices)
    result = Image.new('RGB', (result_width, image_height))

    for i in range(len(slices)):
        result.paste(im=slices[i], box=(slice_width * i, 0))

    try:
        result.save(output_path, quality=qual)
    except (FileNotFoundError, ValueError) as err:
        print("Make sure output_path has a valid file extension: .jpg/.tiff")
        raise err

