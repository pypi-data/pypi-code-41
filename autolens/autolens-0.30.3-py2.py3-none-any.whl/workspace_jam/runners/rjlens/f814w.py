import os

import autofit as af
import autolens as al


# Welcome to the pipeline runner. This tool allows you to load strong lens data, and pass it to pipelines for a
# PyAutoLens analysis. To show you around, we'll load up some example instrument and run it through some of the example
# pipelines that come distributed with PyAutoLens.

# The runner is supplied as both this Python script and a Juypter notebook. Its up to you which you use - I personally
# prefer the python script as provided you keep it relatively small, its quick and easy to comment out different lens
# names and pipelines to perform different analyses. However, notebooks are a tidier way to manage visualization - so
# feel free to use notebooks. Or, use both for a bit, and decide your favourite!

# The pipeline runner is fairly self explanatory. Make sure to checkout the pipelines in the
#  workspace/pipelines/examples/ folder - they come with detailed descriptions of what they do. I hope that you'll
# expand on them for your own personal scientific needs

# It is convenient to specify the data type and data name as a string, so that if the pipeline is applied to multiple
# images we don't have to change all of the path entries in the load_ccd_data_from_fits function below.

# Setup the path to the workspace, using a relative directory name.
workspace_path = "{}/../../".format(os.path.dirname(os.path.realpath(__file__)))
output_path = workspace_path + "../../outputs/PyAutoLens/"
af.conf.instance = af.conf.Config(
    config_path=workspace_path + "config", output_path=output_path
)

data_name = "rjlens"
data_filter = "f814w"

pixel_scale = 0.04

# Create the path where the data will be loaded from, which in this case is
# '/workspace/data/example/lens_light_and_x1_source/'
data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=["data", data_name, data_filter]
)

ccd_data = al.load_ccd_data_from_fits(
    image_path=data_path + "image.fits",
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    pixel_scale=pixel_scale,
)

mask = al.Mask.circular(
    shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, radius_arcsec=3.7
)

positions = al.load_positions(positions_path=data_path + "positions.dat")

data_name = "rjlens_hyper"

pipeline_settings = al.PipelineSettingsHyper(
    hyper_galaxies=True,
    hyper_background_noise=True,
    include_shear=True,
    fix_lens_light=False,
    align_bulge_disk_centre=False,
    align_bulge_disk_phi=False,
    align_bulge_disk_axis_ratio=False,
)

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
    phase_folders=[data_name, data_filter],
    positions_threshold=1.0,
)

pipeline_inversion = lens_bulge_disk_sie__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_name, data_filter],
    positions_threshold=1.0,
)
pipeline_power_law = lens_bulge_disk_power_law__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_name, data_filter],
    positions_threshold=1.0,
)

pipeline = pipeline_initialize + pipeline_inversion + pipeline_power_law

pipeline.run(data=ccd_data, mask=mask, positions=positions)
