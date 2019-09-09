from autolens.array import grids
from autolens.data.instrument import interferometer
from autolens.data import fourier_transform as ft

import numpy as np
import time
import os

test_path = "{}/../".format(os.path.dirname(os.path.realpath(__file__)))
data_path = test_path + "data/uvplane/"

interferometer_data = interferometer.load_interferometer_data_from_fits(
    image_path=data_path + "image.fits",
    pixel_scale=0.05,
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    primary_beam_path=data_path + "primary_beam.fits",
    real_visibilities_path=data_path + "real_visibilities.fits",
    imaginary_visibilities_path=data_path + "imaginary_visibilities.fits",
    visibilities_noise_map_path=data_path + "visibilities_noise_map.fits",
    u_wavelengths_path=data_path + "u_wavelengths.fits",
    v_wavelengths_path=data_path + "v_wavelengths.fits",
    renormalize_psf=False,
    renormalize_primary_beam=False,
)

print(interferometer_data.uv_wavelengths)
stop

repeats = 1

visibilities = len(interferometer_data.visibilities)

grid = grids.Grid.from_shape_pixel_scale_and_sub_grid_size(
    shape=interferometer_data.image.shape,
    pixel_scale=interferometer_data.pixel_scale,
    sub_grid_size=1,
)
grid_radians = grid.in_radians

image_pixels = grid.shape[0] * grid.shape[1]
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

image_1d = np.ones(shape=(image_pixels))

transformer = ft.Transformer(
    uv_wavelengths=interferometer_data.uv_wavelengths, grid_radians=grid_radians
)

print(transformer.preload_real_transforms[0, :])
print(transformer.preload_real_transforms[1, :])
print(transformer.preload_real_transforms[2, :])
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
