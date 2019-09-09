import autolens as al

grid = al.Grid.from_shape_pixel_scale_and_sub_grid_size(
    shape=(100, 100), pixel_scale=0.05, sub_grid_size=16
)

sie = al.mass_profiles.EllipticalIsothermalKormann(
    centre=(0.0, 0.0), einstein_radius=2.0, axis_ratio=0.2, phi=45.0
)
#  sie = al.mass_profiles.EllipticalIsothermal(centre=(0.0, 0.0), einstein_radius=1.0, axis_ratio=0.2, phi=45.0)

convergence_via_jacobian = sie.convergence_via_jacobian_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)
al.array_plotters.plot_array(
    array=convergence_via_jacobian,
    title="Kormann via Deflections & Jacobian",
    norm_max=1.2,
)

convergence = sie.convergence_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)
al.array_plotters.plot_array(
    array=convergence, title="Kormann Convergence", norm_max=1.2
)

deflections_via_jacobian = sie.deflections_via_potential_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)[:, :, 0]
deflections_via_jacobian = al.ScaledSquarePixelArray(
    array=deflections_via_jacobian, pixel_scale=0.05
)
al.array_plotters.plot_array(
    array=deflections_via_jacobian, title="Kormann via Deflections via Potential"
)

deflections = sie.deflections_from_grid(
    grid=grid, return_in_2d=True, return_binned=True
)[:, :, 0]
deflections = al.ScaledSquarePixelArray(array=deflections, pixel_scale=0.05)
al.array_plotters.plot_array(array=deflections, title="Kormann Deflections")
