import autofit as af
from autolens.data.instrument import abstract_data
from autolens.data.instrument import ccd

import os

workspace_path = "{}/../../".format(os.path.dirname(os.path.realpath(__file__)))
af.conf.instance = af.conf.Config(
    config_path=workspace_path + "config", output_path=workspace_path + "output/"
)

data_type = "lens_sample"
data_name = "lens_name"

pixel_scale = 0.00976562

data_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=["data", data_type, data_name]
)

ccd_data = ccd.load_ccd_data_from_fits(
    image_path=data_path + "image.fits",
    psf_path=data_path + "psf.fits",
    noise_map_path=data_path + "noise_map.fits",
    pixel_scale=pixel_scale,
)

from workspace_jam.pipelines.advanced.no_lens_light.initialize import (
    lens_sie_shear_source_sersic,
)
from workspace_jam.pipelines.advanced.no_lens_light.power_law.from_initialize import (
    lens_pl_shear_source_sersic,
)
from workspace_jam.pipelines.advanced.no_lens_light.subhalo.from_power_law import (
    lens_pl_shear_subhalo_source_sersic,
)

pipeline_initialize = lens_sie_shear_source_sersic.make_pipeline(
    phase_folders=[data_type, data_name]
)

pipeline_power_law = lens_pl_shear_source_sersic.make_pipeline(
    phase_folders=[data_type, data_name]
)

pipeline_subhalo = lens_pl_shear_subhalo_source_sersic.make_pipeline(
    phase_folders=[data_type, data_name]
)

pipeline = pipeline_initialize + pipeline_power_law + pipeline_subhalo

pipeline.run(data=ccd_data)
