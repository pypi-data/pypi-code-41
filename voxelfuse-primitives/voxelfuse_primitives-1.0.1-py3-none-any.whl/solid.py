"""
Copyright 2018-2019
Dan Aukes, Cole Brauer

Extends the VoxelModel class with functions for generating linkages
"""

import numpy as np
from voxelfuse.voxel_model import VoxelModel
from voxelfuse.materials import materials

class Solid(VoxelModel):
    @classmethod
    def cube(cls, size = 1, coords = (0, 0, 0), material = 1):
        model_data = np.ones((size, size, size, len(materials)+1))
        model = cls(model_data, coords[0], coords[1], coords[2])
        model = model.setMaterial(material)
        return model

    @classmethod
    def cuboid(cls, size = (1, 1, 1), coords = (0, 0, 0), material=1):
        model_data = np.ones((size[1], size[2], size[0], len(materials) + 1))
        model = cls(model_data, coords[0], coords[1], coords[2])
        model = model.setMaterial(material)
        return model

    @classmethod
    def sphere(cls, radius = 1, coords = (0, 0, 0), material = 1):
        diameter = (radius*2) + 1
        model_data = np.zeros((diameter, diameter, diameter, len(materials)+1))

        for x in range(diameter):
            for y in range(diameter):
                for z in range(diameter):
                    xd = (x - radius)
                    yd = (y - radius)
                    zd = (z - radius)
                    r = np.sqrt(xd**2 + yd**2 + zd**2)

                    if r < (radius + .5):
                        model_data[y, z, x].fill(1)

        model = cls(model_data, coords[0]-radius, coords[1]-radius, coords[2]-radius)
        model = model.setMaterial(material)
        return model

    @classmethod
    def cylinder(cls, radius=1, height=1, coords=(0, 0, 0), material=1):
        diameter = (radius * 2) + 1
        model_data = np.zeros((diameter, 1, diameter, len(materials) + 1))

        for x in range(diameter):
            for y in range(diameter):
                    xd = (x - radius)
                    yd = (y - radius)
                    r = np.sqrt(xd ** 2 + yd ** 2)

                    if r < (radius + .5):
                        model_data[y, 0, x].fill(1)

        model_data = np.repeat(model_data, height, 1)

        model = cls(model_data, coords[0] - radius, coords[1] - radius, coords[2])
        model = model.setMaterial(material)
        return model

    @classmethod
    def cone(cls, min_radius=0, max_radius=4, height=5, coords=(0, 0, 0), material=1):
        max_diameter = (max_radius*2)+1
        model_data = np.zeros((max_diameter, height, max_diameter, len(materials) + 1))

        for z in range(height):
            radius = (abs(max_radius - min_radius) * (((height-1) - z)/(height-1))) + min_radius

            for x in range(max_diameter):
                for y in range(max_diameter):
                    xd = (x - max_radius)
                    yd = (y - max_radius)
                    r = np.sqrt(xd ** 2 + yd ** 2)

                    if r < (radius + .5):
                        model_data[y, z, x].fill(1)

        model = cls(model_data, coords[0] - max_radius, coords[1] - max_radius, coords[2])
        model = model.setMaterial(material)
        return model

    @classmethod
    def pyramid(cls, min_radius=0, max_radius=4, height=5, coords=(0, 0, 0), material=1):
        max_diameter = (max_radius * 2) + 1
        model_data = np.zeros((max_diameter, height, max_diameter, len(materials) + 1))

        for z in range(height):
            radius = round((abs(max_radius - min_radius) * (z / (height - 1))))

            if radius == 0:
                model_data[:, z, :].fill(1)
            else:
                model_data[radius:-radius, z, radius:-radius].fill(1)

        model = cls(model_data, coords[0] - max_radius, coords[1] - max_radius, coords[2])
        model = model.setMaterial(material)
        return model