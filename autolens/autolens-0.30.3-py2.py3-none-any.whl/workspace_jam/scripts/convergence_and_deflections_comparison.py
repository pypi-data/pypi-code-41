import autolens as al
import numpy as np

grid = al.Grid.from_shape_pixel_scale_and_sub_grid_size(
    shape=(100, 100), pixel_scale=0.05, sub_grid_size=2
)

sie = al.mass_profiles.EllipticalIsothermalKormann(
    centre=(0.0, 0.0), einstein_radius=1.0, axis_ratio=0.2, phi=45.0
)
convergence_0 = sie.deflections_from_grid(grid=grid, return_in_2d=True)[:, :, 0]
deflections_y_0 = al.ScaledSquarePixelArray(array=convergence_0, pixel_scale=0.05)

sie = al.mass_profiles.EllipticalIsothermalKormann(
    centre=(0.0, 0.0), einstein_radius=1.0, axis_ratio=0.2, phi=135.0
)
convergence_1 = sie.deflections_from_grid_2(grid=grid, return_in_2d=True)[:, :, 0]
deflections_y_1 = al.ScaledSquarePixelArray(array=convergence_1, pixel_scale=0.05)

residuals = convergence_0 - convergence_1

print(np.max(residuals))
residuals = al.ScaledSquarePixelArray(array=residuals, pixel_scale=0.05)
al.array_plotters.plot_array(array=residuals)
