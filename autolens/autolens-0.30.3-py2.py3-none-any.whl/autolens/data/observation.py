import autofit as af
from autolens.data.instrument import abstract_data
from autolens.data.instrument import ccd
from autolens.array import grids
from autolens.lens import ray_tracing
from autolens.data.plotters import ccd_plotters


class CCDObservation(object):
    def __init__(self, shape, pixel_scale, psf, exposure_time, background_sky_level):
        """A class representing a CCD observation, using the shape of the image, the pixel scale,
        psf, exposure time, etc.

        Parameters
        ----------
        shape : (int, int)
            The shape of the observation. Note that we do not simulate a full CCD frame (e.g. 2000 x 2000 pixels for \
            Hubble imaging), but instead just a cut-out around the strong lens.
        pixel_scale : float
            The size of each pixel in arc seconds.
        psf : PSF
            An array describing the PSF kernel of the image.
        exposure_time : float
            The exposure time of an observation using this instrument.
        background_sky_level : float
            The level of the background sky of an observationg using this instrument.
        """
        self.shape = shape
        self.pixel_scale = pixel_scale
        self.psf = psf
        self.exposure_time = exposure_time
        self.background_sky_level = background_sky_level

    def simulate_ccd_data_from_galaxies(
        self,
        galaxies,
        sub_grid_size=16,
        add_noise=True,
        noise_if_add_noise_false=0.1,
        noise_seed=-1,
        should_plot_ccd_data=False,
    ):
        """Simulate CCD instrument for this instrument, as follows:

        1)  Setup the image-plane al.ogrid of the CCD array, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated CCD instrument.

        3) Simulate the CCD instrument, using a special image which ensures edge-effects don't
           degrade simulation of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_ccd bool is True.

        5) Output the data to .fits format if a data_path and data_name are specified. Otherwise, return the simulated \
           ccd instrument instance."""

        grid = grids.Grid.from_shape_pixel_scale_and_sub_grid_size(
            shape=self.shape,
            pixel_scale=self.psf.pixel_scale,
            sub_grid_size=sub_grid_size,
        )

        tracer = ray_tracing.Tracer.from_galaxies(galaxies=galaxies)

        ccd_data = ccd.SimulatedCCDData.from_tracer_grid_and_exposure_arrays(
            tracer=tracer,
            grid=grid,
            pixel_scale=self.pixel_scale,
            exposure_time=self.exposure_time,
            psf=self.psf,
            background_sky_level=self.background_sky_level,
            add_noise=add_noise,
            noise_if_add_noise_false=noise_if_add_noise_false,
            noise_seed=noise_seed,
        )

        if should_plot_ccd_data:
            ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data)

        return ccd_data

    def simulate_ccd_data_from_galaxies_and_write_to_fits(
        self,
        galaxies,
        data_path,
        data_name,
        sub_grid_size=16,
        add_noise=True,
        noise_if_add_noise_false=0.1,
        noise_seed=-1,
        should_plot_ccd_data=False,
    ):
        """Simulate CCD instrument for this instrument, as follows:

        1)  Setup the image-plane al.ogrid of the CCD array, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated CCD instrument.

        3) Simulate the CCD instrument, using a special image which ensures edge-effects don't
           degrade simulation of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_ccd bool is True.

        5) Output the data to .fits format if a data_path and data_name are specified. Otherwise, return the simulated \
           ccd instrument instance."""

        ccd_data = self.simulate_ccd_data_from_galaxies(
            galaxies=galaxies,
            sub_grid_size=sub_grid_size,
            add_noise=add_noise,
            noise_if_add_noise_false=noise_if_add_noise_false,
            noise_seed=noise_seed,
            should_plot_ccd_data=should_plot_ccd_data,
        )

        data_output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
            path=data_path, folder_names=[data_name]
        )

        ccd.output_ccd_data_to_fits(
            ccd_data=ccd_data,
            image_path=data_output_path + "image.fits",
            psf_path=data_output_path + "psf.fits",
            noise_map_path=data_output_path + "noise_map.fits",
            exposure_time_map_path=data_output_path + "exposure_time_map.fits",
            background_noise_map_path=data_output_path + "background_noise_map.fits",
            poisson_noise_map_path=data_output_path + "poisson_noise_map.fits",
            background_sky_map_path=data_output_path + "background_sky_map.fits",
            overwrite=True,
        )

    @classmethod
    def lsst(
        cls,
        shape=(101, 101),
        pixel_scale=0.2,
        psf_shape=(31, 31),
        psf_sigma=0.5,
        exposure_time=100.0,
        background_sky_level=1.0,
    ):
        """Default settings for an observation with the Large Synotpic Survey Telescope.

        This can be customized by over-riding the default input values."""
        psf = abstract_data.PSF.from_gaussian(
            shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale
        )
        return CCDObservation(
            shape=shape,
            pixel_scale=pixel_scale,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
        )

    @classmethod
    def euclid(
        cls,
        shape=(151, 151),
        pixel_scale=0.1,
        psf_shape=(31, 31),
        psf_sigma=0.1,
        exposure_time=565.0,
        background_sky_level=1.0,
    ):
        """Default settings for an observation with the Euclid space satellite.

        This can be customized by over-riding the default input values."""
        psf = abstract_data.PSF.from_gaussian(
            shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale
        )
        return CCDObservation(
            shape=shape,
            pixel_scale=pixel_scale,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
        )

    @classmethod
    def hst(
        cls,
        shape=(251, 251),
        pixel_scale=0.05,
        psf_shape=(31, 31),
        psf_sigma=0.05,
        exposure_time=2000.0,
        background_sky_level=1.0,
    ):
        """Default settings for an observation with the Hubble Space Telescope.

        This can be customized by over-riding the default input values."""
        psf = abstract_data.PSF.from_gaussian(
            shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale
        )
        return CCDObservation(
            shape=shape,
            pixel_scale=pixel_scale,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
        )

    @classmethod
    def hst_up_sampled(
        cls,
        shape=(401, 401),
        pixel_scale=0.03,
        psf_shape=(31, 31),
        psf_sigma=0.05,
        exposure_time=2000.0,
        background_sky_level=1.0,
    ):
        """Default settings for an observation with the Hubble Space Telescope which has been upscaled to a higher \
        pixel-scale to better sample the PSF.

        This can be customized by over-riding the default input values."""
        psf = abstract_data.PSF.from_gaussian(
            shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale
        )
        return CCDObservation(
            shape=shape,
            pixel_scale=pixel_scale,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
        )

    @classmethod
    def keck_adaptive_optics(
        cls,
        shape=(751, 751),
        pixel_scale=0.01,
        psf_shape=(31, 31),
        psf_sigma=0.025,
        exposure_time=1000.0,
        background_sky_level=1.0,
    ):
        """Default settings for an observation using Keck Adaptive Optics imaging.

        This can be customized by over-riding the default input values."""
        psf = abstract_data.PSF.from_gaussian(
            shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale
        )
        return CCDObservation(
            shape=shape,
            pixel_scale=pixel_scale,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
        )
