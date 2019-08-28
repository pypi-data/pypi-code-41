
import trimesh
import numpy as np

mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [0, 0, 1], [0, 1, 0]],
                       faces=[[0, 1, 2]])


mesh = trimesh.creation.icosphere()

ray_origins = np.array([[0, 0, -3],
                        [2, 2, -3]])
ray_directions = np.array([[0, 0, 1],
                           [0, 0, 1]])


locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=ray_origins,
        ray_directions=ray_directions)

print('The rays hit the mesh at coordinates:\n', locations)