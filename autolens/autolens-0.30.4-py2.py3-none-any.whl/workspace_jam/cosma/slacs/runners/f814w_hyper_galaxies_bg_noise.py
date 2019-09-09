import os
import sys

### AUTOFIT + CONFIG SETUP ###

import autofit as af

cosma_username = "dc-nigh1"
cosma_path = "/cosma6/data/dp004/dc-nigh1/"
cosma_data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    cosma_path, folder_names=["data"]
)
cosma_output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    cosma_path, folder_names=["output", "slacs_hyper"]
)

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


# Lets take a look at a Cosma batch script, which can be found at 'workspace/runners/cosma/batch/pipeline_runner_cosma'.
# When we submit a PyAutoLens job to Cosma, we submit a 'batch' of jobs, whereby each job will run on one CPU of Cosma.
# Thus, if our lens sample contains, lets say, 17 lenses, we'd submit 17 jobs at the same time where each job applies
# our pipeline to each image.

# The fifth line of this batch script - '#SBATCH --array=1-17' is what species this. Its telling Cosma we're going to
# run 17 jobs, and the id's of those jobs will be numbered from 1 to 17. Infact, these ids are passed to this runner,
# and we'll use them to ensure that each jobs loads a different image. Lets get the cosma array id for our job.
cosma_array_id = int(sys.argv[1])

# Now, I just want to really drive home what the above line is doing. For every job we run on Cosma, the cosma_array_id
# will be different. That is, job 1 will get a cosma_array_id of 1, job 2 will get an id of 2, and so on. This is our
# only unique identifier of every job, thus its our only hope of specifying for each job which image they load!

# Fortunately, we're used to specifying the lens name as a string, so that our pipeline can be applied to multiple
# images with ease. On Cosma, we can apply the same logic, but put these strings in a list such that each Cosma job
# loads a different lens name based on its ID. neat, huh?

data_type = "slacs_jam"

data_filter = "F814W"

data_name = []
data_name.append("")  # Task number beings at 1, so keep index 0 blank
data_name.append("slacs0216-0813")  # Index 1
data_name.append("slacs0252+0039")  # Index 2
data_name.append("slacs0737+3216")  # Index 3
data_name.append("slacs0912+0029")  # Index 4
data_name.append("slacs0959+4410")  # Index 5
data_name.append("slacs0959+4416")  # Index 5
data_name.append("slacs1205+4910")  # Index 6
data_name.append("slacs1250+0523")  # Index 7
data_name.append("slacs1402+6321")  # Index 8
data_name.append("slacs1420+6019")  # Index 9
data_name.append("slacs1430+4105")  # Index 10
data_name.append("slacs1627+0053")  # Index 11
data_name.append("slacs1630+4520")  # Index 12
data_name.append("slacs2238-0754")  # Index 13
data_name.append("slacs2300+0022")  # Index 14
data_name.append("slacs2303+1422")  # Index 15

data_name = data_name[cosma_array_id]

pixel_scale = 0.03  # Make sure your pixel scale is correct!

# We now use the lens_name list to load the image on each job, noting that in this example I'm assuming our lenses are
# on the Cosma instrument directory folder called 'slacs'
data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=cosma_data_path, folder_names=[data_type, data_name]
)

ccd_data = al.load_ccd_data_from_fits(
    image_path=data_path + "F814W_image.fits",
    psf_path=data_path + "F814W_psf.fits",
    noise_map_path=data_path + "F814W_noise_map.fits",
    pixel_scale=pixel_scale,
    resized_ccd_shape=(301, 301),
    resized_psf_shape=(15, 15),
)

mask = al.load_mask_from_fits(
    mask_path=data_path + "mask.fits", pixel_scale=pixel_scale
)
mask = mask.resized_scaled_array_from_array(new_shape=(301, 301))

positions = al.load_positions(positions_path=data_path + "positions.dat")

pipeline_settings = al.PipelineSettingsHyper(
    hyper_galaxies=True,
    hyper_image_sky=False,
    hyper_background_noise=True,
    include_shear=True,
    align_bulge_disk_centre=True,
    disk_as_sersic=True,
    pixelization=al.pixelizations.VoronoiBrightnessImage,
    regularization=al.regularization.AdaptiveBrightness,
)


# Running a pipeline is exactly the same as we're used to. We import it, make it, and run it, noting that we can
# use the lens_name's to ensure each job outputs its results to a different directory.

from workspace_jam.pipelines.hyper.with_lens_light.bulge_disk.initialize import (
    lens_bulge_disk_sie__source_sersic,
)
from workspace_jam.pipelines.hyper.with_lens_light.bulge_disk.inversion.from_initialize import (
    lens_bulge_disk_sie__source_inversion,
)
from workspace_jam.pipelines.hyper.with_lens_light.bulge_disk.power_law.from_inversion import (
    lens_bulge_disk_power_law__source_inversion,
)

pipeline_initialize = lens_bulge_disk_sie__source_sersic.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_filter, data_name],
    positions_threshold=1.0,
)

pipeline_inversion = lens_bulge_disk_sie__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_filter, data_name],
    positions_threshold=1.0,
)

pipeline_power_law = lens_bulge_disk_power_law__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_filter, data_name],
    positions_threshold=0.5,
)

pipeline = pipeline_initialize + pipeline_inversion + pipeline_power_law

pipeline.run(data=ccd_data, mask=mask, positions=positions)
