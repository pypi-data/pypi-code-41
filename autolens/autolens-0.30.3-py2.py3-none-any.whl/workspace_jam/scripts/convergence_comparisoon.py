import autolens as al

grid = al.Grid.from_shape_pixel_scale_and_sub_grid_size(
    shape=(100, 100), pixel_scale=0.05, sub_grid_size=16
)

sie = al.mass_profiles.EllipticalIsothermalKormann(
    centre=(0.0, 0.0), einstein_radius=1.0, axis_ratio=0.5, phi=0.0
)
# sie = al.mass_profiles.EllipticalIsothermal(centre=(0.0, 0.0), einstein_radius=1.0, axis_ratio=0.5, phi=0.0)
convergence_0 = sie.convergence_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)
convergence_1 = sie.convergence_via_jacobian_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)

residuals = convergence_0 - convergence_1

mask = al.Mask.circular_annular(
    shape=(100, 100), pixel_scale=0.05, inner_radius_arcsec=0.5, outer_radius_arcsec=2.5
)
al.array_plotters.plot_array(array=residuals, mask=mask, extract_array_from_mask=True)
