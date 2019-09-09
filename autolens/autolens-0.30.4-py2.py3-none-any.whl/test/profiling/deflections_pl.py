import time

from autolens.model.profiles import mass_profiles as mp
from autolens.lens import lens_data as ld
from autolens.array import mask as msk

from test.simulation import simulation_util

# Although we could test the deflection angles without using an image (e.g. by just making a grid), we have chosen to
# set this test up using an image and mask. This gives run-time numbers that can be easily related to an actual lens
# analysis

sub_grid_size = 4
radius_arcsec = 3.0

print("sub grid size = " + str(sub_grid_size))
print("circular mask radius = " + str(radius_arcsec) + "\n")

for data_resolution in ["LSST", "Euclid", "HST", "HST_Up", "AO"]:

    ccd_data = simulation_util.load_test_ccd_data(
        data_type="lens_mass__source_smooth",
        data_resolution=data_resolution,
        psf_shape=(3, 3),
    )
    mask = al.Mask.circular(
        shape=ccd_data.shape,
        pixel_scale=ccd_data.pixel_scale,
        radius_arcsec=radius_arcsec,
    )
    lens_data = al.LensData(ccd_data=ccd_data, mask=mask, sub_grid_size=sub_grid_size)

    print("Deflection angle run times for image type " + data_resolution + "\n")
    print("Number of points = " + str(lens_data.grid.shape[0]) + "\n")

    ### EllipticalIsothermal ###

    mass_profile = al.mass_profiles.EllipticalIsothermal(
        centre=(0.0, 0.0), axis_ratio=0.8, phi=45.0, einstein_radius=1.0
    )

    start = time.time()
    mass_profile.deflections_from_grid(grid=lens_data.grid)
    diff = time.time() - start
    print("EllipticalIsothermal time = {}".format(diff))

    ### EllipticalPowerLaw (slope = 1.5) ###

    mass_profile = al.mass_profiles.EllipticalPowerLaw(
        centre=(0.0, 0.0), axis_ratio=0.8, phi=45.0, einstein_radius=1.0, slope=1.5
    )

    start = time.time()
    mass_profile.deflections_from_grid(grid=lens_data.grid)
    diff = time.time() - start
    print("EllipticalPowerLaw (slope = 1.5) time = {}".format(diff))

    ### EllipticalPowerLaw (slope = 2.5) ###

    mass_profile = al.mass_profiles.EllipticalPowerLaw(
        centre=(0.0, 0.0), axis_ratio=0.8, phi=45.0, einstein_radius=1.0, slope=2.5
    )

    start = time.time()
    mass_profile.deflections_from_grid(grid=lens_data.grid)
    diff = time.time() - start
    print("EllipticalPowerLaw (slope = 2.5) time = {}".format(diff))
