from autolens.data.instrument import abstract_data
from autolens.data.instrument import ccd
from autolens.array import grids
from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import light_profiles as lp
from autolens.data.plotters import ccd_plotters

import os

# This tool allows one to make simulated data-sets of strong lenses, which can be used to test example pipelines and
# investigate strong lens modeling on data-sets where the 'true' answer is known.

# Setup the path to the workspace, using a relative directory name.
workspace_path = "{}/../../".format(os.path.dirname(os.path.realpath(__file__)))

# The 'data name' is the name of the data folder and 'data_name' the folder the data is stored in, e.g:

# The image will be output as '/workspace/data/data_type/data_name/image.fits'.
# The noise-map will be output as '/workspace/data/data_type/data_name/lens_name/noise_map.fits'.
# The psf will be output as '/workspace/data/data_type/data_name/psf.fits'.

# (these files are already in the workspace and are remade running this script)
data_type = "example"
data_name = "lens_light_and_x1_source"

# Create the path where the data will be output, which in this case is
# '/workspace/data/example/lens_light_and_x1_source/'
data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=["data", data_type, data_name]
)

# The pixel scale of the image to be simulated
pixel_scale = 0.1

# Simulate a simple Gaussian PSF for the image.
psf = abstract_data.PSF.from_gaussian(
    shape=(11, 11), sigma=0.1, pixel_scale=pixel_scale
)

# Setup the image-plane al.ogrid of the CCD array which will be used for generating the image of the
# simulated strong lens. The sub-grid size of 20x20 ensures we fully resolve the central regions of the lens and source
# galaxy light.
image_plane_grid = grids.Grid.from_shape_pixel_scale_and_sub_grid_size(
    shape=(100, 100), pixel_scale=pixel_scale, sub_grid_size=16
)

# Setup the lens galaxy's light (elliptical Sersic), mass (SIE+Shear) and source galaxy light (elliptical Sersic) for
# this simulated lens.
lens_galaxy = g.Galaxy(
    redshift=0.5,
    light=al.light_profiles.EllipticalSersic(
        centre=(0.0, 0.0),
        axis_ratio=0.9,
        phi=45.0,
        intensity=1.0,
        effective_radius=0.8,
        sersic_index=4.0,
    ),
)


# Use these galaxies to setup a tracer, which will generate the image for the simulated CCD instrument.
tracer = ray_tracing.Tracer.from_galaxies(galaxies=[lens_galaxy])

# Simulate the CCD instrument, remembering that we use a special image which ensures edge-effects don't
# degrade our modeling of the telescope optics (e.g. the PSF convolution).
ccd = ccd.SimulatedCCDData.from_image_and_exposure_arrays(
    array=tracer.padded_profile_image_2d_from_grid_and_psf_shape,
    pixel_scale=pixel_scale,
    exposure_time=300.0,
    psf=psf,
    background_sky_level=0.1,
    add_noise=False,
)

# Lets plot the simulated CCD instrument before we output it to files.
ccd_plotters.plot_ccd_subplot(ccd_data=ccd)

# Finally, lets output our simulated instrument to the data path as .fits files.
ccd.output_ccd_data_to_fits(
    ccd_data=ccd,
    image_path=data_path + "image.fits",
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    overwrite=True,
)
