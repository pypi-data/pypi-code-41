from autolens import decorator_util
from autolens.data import fourier_transform as ft

import numpy as np
import time

repeats = 1

visibilities = 100000000
image_pixels = 100000
source_pixels = 1000

shape_data = 8 * visibilities
shape_preloads = visibilities * image_pixels * 2
shape_mapping_matrix = visibilities * source_pixels

total_shape = shape_data + shape_preloads + shape_mapping_matrix

print("Data Memory Use (GB) = " + str(shape_data * 8e-9))
print("PreLoad Memory Use (GB) = " + str(shape_preloads * 8e-9))
print("Mapping Matrix Memory Use (GB) = " + str(shape_mapping_matrix * 8e-9))
print("Total Memory Use (GB) = " + str(total_shape * 8e-9))
print()

uv_wavelengths = np.ones(shape=(visibilities, 2))
grid_radians = np.ones(shape=(image_pixels, 2))
image_1d = np.ones(shape=(image_pixels))

transformer = ft.Transformer(
    uv_wavelengths=uv_wavelengths, grid_radians=grid_radians, preload_transform=False
)


@decorator_util.jit()
def interpolation_loop(image_pixels, visibilities):

    for im in range(image_pixels):
        for vis in range(visibilities):
            weight = np.cos(im * vis / 1000000.0) + np.sin(im ** vis)


start = time.time()
for i in range(repeats):
    interpolation_loop(image_pixels=image_pixels, visibilities=visibilities)
diff = time.time() - start
print("Interpolation Loop Time = {}".format(diff / repeats))

stop

start = time.time()
for i in range(repeats):
    transformer.real_visibilities_from_image_1d(image_1d=image_1d)
diff = time.time() - start
print("Real Visibilities Time = {}".format(diff / repeats))

start = time.time()
for i in range(repeats):
    transformer.real_visibilities_via_preload_from_image(image_1d=image_1d)
diff = time.time() - start
print("Real Visibilities PreLoad Time = {}".format(diff / repeats))
