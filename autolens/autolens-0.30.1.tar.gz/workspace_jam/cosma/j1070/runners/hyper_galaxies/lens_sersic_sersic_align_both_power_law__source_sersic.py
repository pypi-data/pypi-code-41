import os
import sys

### AUTOFIT + CONFIG SETUP ###

import autofit as af


import os

### NOTE - if you have not already, complete the setup in 'workspace/runners/cosma/setup' before continuing with this
### cosma pipeline script.

# Welcome to the Cosma pipeline runner. Hopefully, you're familiar with runners at this point, and have been using them
# with PyAutoLens to model lenses on your laptop. If not, I'd recommend you get used to doing that, before trying to
# run PyAutoLens on a super-computer. You need some familiarity with the software and lens modeling before trying to
# model a large sample of lenses on a supercomputer!

# If you are ready, then let me take you through the Cosma runner. It is remarkably similar to the ordinary pipeline
# runners you're used to, however it makes a few changes for running jobs on cosma:

# 1) The data path is over-written to the path '/cosma5/data/autolens/cosma_username/instrument' as opposed to the
#    workspace. As we discussed in the setup, on cosma we don't store our instrument in our workspace.

# 2) The output path is over-written to the path '/cosma5/data/autolens/cosma_username/output' as opposed to
#    the workspace. This is for the same reason as the data.

# Lets use this to setup our cosma path, which is where our instrument and output are stored.
cosma_path = "/cosma5/data/autolens/share/"

# Next, lets use this path to setup the data path, which for this example is named 'example' and found at
# '/cosma5/data/autolens/share/data/example/'
cosma_data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_path, folder_names=["data"]
)

# We'll do the same for our output path, which is '/cosma5/data/autolens/share/output/example/'
cosma_output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_path, folder_names=["output"]
)

# Next, we need the path to our Cosma workspace, which can be generated using a relative path given that our runner is
# located in our Cosma workspace.
workspace_path = "{}/../../../../".format(os.path.dirname(os.path.realpath(__file__)))

# We will use a unique config file for each data-set we model on our super computer. This ensures we can customize the
# analysis of each data-set.
config_path = "{}/../".format(os.path.dirname(os.path.realpath(__file__)))

# Lets now use the above paths to set the config path and output path for our Cosma run.
af.conf.instance = af.conf.Config(
    config_path=config_path + "config", output_path=cosma_output_path
)

### AUTOLENS + DATA SETUP ###

import autolens as al


data_name = "j1070"

pixel_scale = 0.106  # Make sure your pixel scale is correct!

# We now use the data_name to load a the data-set on each job. The statement below combines
# the cosma_data_path and and data_name to read instrument from the following directory:
# '/cosma5/data/autolens/share/data/example/data_name'

data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_data_path, folder_names=[data_name + "_unscaled"]
)

# This loads the CCD imaging data, as per usual.
ccd_data = al.load_ccd_data_from_fits(
    image_path=data_path + "image.fits",
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    pixel_scale=pixel_scale,
)

mask = al.load_mask_from_fits(
    mask_path=data_path + "mask.fits", pixel_scale=pixel_scale
)

positions = al.load_positions(positions_path=data_path + "positions.dat")


### PIPELINE SETTINGS ###

pipeline_settings = al.PipelineSettingsHyper(
    hyper_galaxies=True,
    include_shear=True,
    fix_lens_light=False,
    align_bulge_disk_centre=True,
    align_bulge_disk_phi=True,
    align_bulge_disk_axis_ratio=False,
    disk_as_sersic=True,
)

from workspace_jam.pipelines.hyper.with_lens_light.bulge_disk.initialize import (
    lens_bulge_disk_sie__source_sersic,
)
from workspace_jam.pipelines.hyper.with_lens_light.bulge_disk.power_law.from_initialize import (
    lens_bulge_disk_power_law__source_sersic,
)

pipeline_initialize = lens_bulge_disk_sie__source_sersic.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_name],
    positions_threshold=1.0,
)

pipeline_power_law = lens_bulge_disk_power_law__source_sersic.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_name],
    positions_threshold=1.0,
)

pipeline = pipeline_initialize + pipeline_power_law

pipeline.run(data=ccd_data, mask=mask, positions=positions)
