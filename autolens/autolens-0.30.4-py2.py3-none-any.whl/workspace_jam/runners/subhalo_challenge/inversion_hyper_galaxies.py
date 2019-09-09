import autofit as af
import autolens as al

import os

# Setup the path to the workspace, using a relative directory name.
workspace_path = "{}/../../".format(os.path.dirname(os.path.realpath(__file__)))
output_path = workspace_path + "../../outputs/PyAutoLens/subhalo_challenge"

af.conf.instance = af.conf.Config(
    config_path=workspace_path + "config", output_path=output_path
)

data_type = "analytic_psf"

data_level = "level_0"

data_name = "large_hi_sn_system_1"
data_name = "small_hi_sn_system_1"

# data_level = 'level_1'
# data_name = 'large_hi_sn_system_1'
# data_name = 'large_hi_sn_system_2'
# data_name = 'large_md_sn_system_1'
# data_name = 'large_md_sn_system_2'
# data_name = 'large_lo_sn_system_1'
# data_name = 'large_lo_sn_system_2'
# data_name = 'small_hi_sn_system_1'
# data_name = 'small_hi_sn_system_2'
# data_name = 'small_md_sn_system_1'
# data_name = 'small_md_sn_system_2'
# data_name = 'small_lo_sn_system_1'
# data_name = 'small_lo_sn_system_2'

pixel_scale = 0.00976562

data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path,
    folder_names=["data", "subhalo_challenge", data_type, data_level, data_name],
)

resized_shape = (700, 700)

ccd_data = al.load_ccd_data_from_fits(
    image_path=data_path + "image.fits",
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    pixel_scale=pixel_scale,
    resized_ccd_shape=resized_shape,
    resized_psf_shape=(9, 9),
)

mask = al.load_mask_from_fits(
    mask_path=data_path + "mask_irregular.fits", pixel_scale=pixel_scale
)

mask = mask.resized_scaled_array_from_array(new_shape=resized_shape)

positions = al.load_positions(positions_path=data_path + "positions.dat")

pipeline_settings = al.PipelineSettingsHyper(
    hyper_galaxies=True,
    hyper_image_sky=False,
    hyper_background_noise=False,
    include_shear=True,
    pixelization=al.pixelizations.VoronoiBrightnessImage,
    regularization=al.regularization.AdaptiveBrightness,
)

from workspace_jam.pipelines.hyper.no_lens_light.initialize import (
    lens_sie__source_sersic,
)
from workspace_jam.pipelines.hyper.no_lens_light.inversion.from_initialize import (
    lens_sie__source_inversion,
)
from workspace_jam.pipelines.hyper.no_lens_light.power_law.from_inversion import (
    lens_power_law__source_inversion,
)

from workspace_jam.pipelines.hyper.no_lens_light.subhalo.from_power_law import (
    lens_power_law__subhalo_nfw__source_inversion,
)

pipeline_initialize = lens_sie__source_sersic.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_type, data_level, data_name],
    positions_threshold=1.0,
)

pipeline_inversion = lens_sie__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_type, data_level, data_name],
    positions_threshold=1.0,
    inversion_pixel_limit=800,
)

pipeline_power_law = lens_power_law__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_type, data_level, data_name],
    positions_threshold=0.2,
    inversion_pixel_limit=800,
)

pipeline_subhalo = lens_power_law__subhalo_nfw__source_inversion.make_pipeline(
    pipeline_settings=pipeline_settings,
    phase_folders=[data_type, data_level, data_name],
    positions_threshold=0.2,
    inversion_pixel_limit=800,
)

pipeline = (
    pipeline_initialize + pipeline_inversion + pipeline_power_law + pipeline_subhalo
)

pipeline.run(data=ccd_data, mask=mask, positions=positions)
