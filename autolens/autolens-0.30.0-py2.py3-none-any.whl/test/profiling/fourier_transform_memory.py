from autolens.data import fourier_transform as ft

import numpy as np
import time

repeats = 1

visibilities = int(1e7)
image_pixels = int(1e5)
source_pixels = int(1e3)

shape_data = 8 * visibilities
shape_preloads = visibilities * image_pixels * 2
shape_mapping_matrix = (visibilities * source_pixels) + (image_pixels * source_pixels)

total_shape = shape_data + shape_preloads + shape_mapping_matrix

print("Data Memory Use (GB) = " + str(shape_data * 8e-9))
print("PreLoad Memory Use (GB) = " + str(shape_preloads * 8e-9))
print("Mapping Matrix Memory Use (GB) = " + str(shape_mapping_matrix * 8e-9))
print("Total Memory Use (GB) = " + str(total_shape * 8e-9))
