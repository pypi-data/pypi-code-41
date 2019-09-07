from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import mass_profiles as mp
from autolens.model.profiles import light_profiles as lp
from autolens.array import grids
from autolens.data.instrument import abstract_data
import numpy as np
import matplotlib.pyplot as plt

pixel_scale = 0.05

psf = abstract_data.PSF.from_gaussian(
    shape=(11, 11), sigma=0.1, pixel_scale=pixel_scale
)

grid = grids.grid_stack_for_simulation(
    shape=(200, 200), pixel_scale=pixel_scale, sub_grid_size=1
)

g0 = g.Galaxy(
    mass_profile=al.mass_profiles.SphericalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.6
    ),
    redshift=0.5,
)

source_galaxy = g.Galaxy(
    light=al.light_profiles.EllipticalSersic(
        centre=(0.0, 0.0),
        axis_ratio=1.0,
        phi=0.0,
        intensity=1.0,
        effective_radius=1.0,
        sersic_index=2.5,
    ),
    redshift=1.0,
)

tracer0 = ray_tracing.Tracer(galaxies=[g0, source_galaxy])

redshift_1 = 0.5
subhalo_1 = g.Galaxy(
    mass=al.mass_profiles.SphericalNFW(
        centre=(1.6, 0.0), kappa_s=0.3, scale_radius=0.5
    ),
    redshift=redshift_1,
)

tracer1 = ray_tracing.Tracer(galaxies=[g0, source_galaxy, subhalo_1])

redshift_2 = 0.8
subhalo_2 = g.Galaxy(
    mass=al.mass_profiles.SphericalNFW(
        centre=(1.6, 0.0), kappa_s=0.3, scale_radius=0.5
    ),
    redshift=redshift_2,
)

tracer2 = ray_tracing.Tracer(galaxies=[g0, source_galaxy, subhalo_2])

redshift_3 = 0.9
traced_grid = tracer0.grid_at_redshift_from_grid_and_redshift(
    grid=np.array([[1.6, 0.0]]), redshift=redshift_3
)

subhalo_3 = g.Galaxy(
    mass=al.mass_profiles.SphericalNFW(
        centre=traced_grid, kappa_s=0.3, scale_radius=0.5
    ),
    light=al.light_profiles.EllipticalSersic(
        centre=traced_grid,
        axis_ratio=1.0,
        phi=0.0,
        intensity=1.0,
        effective_radius=1.0,
        sersic_index=2.5,
    ),
    redshift=redshift_3,
)


tracer3 = ray_tracing.Tracer(galaxies=[g0, source_galaxy, subhalo_3])

fig, axes = plt.subplots(3, 1, figsize=(4, 12))
axes[0].imshow(tracer1.profile_image_plane_image_2d)
axes[1].imshow(tracer2.profile_image_plane_image_2d)
axes[2].imshow(tracer3.profile_image_plane_image_2d)
plt.tight_layout()
plt.show()
