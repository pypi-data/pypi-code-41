from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name='chamferdist',
    version='0.1.0',
    description='A pytorch module to compute Chamfer distance between \
        two point sets (pointclouds).', 
    ext_modules=[
        CUDAExtension('chamferdistcuda', [
            'chamferdist/chamfer_cuda.cpp',
            'chamferdist/chamfer.cu',
        ]),
    ],
    cmdclass={
        'build_ext': BuildExtension
    })
