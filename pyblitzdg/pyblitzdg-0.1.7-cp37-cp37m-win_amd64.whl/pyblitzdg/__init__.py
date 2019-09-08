# wrapper to load bundled deps in proper order, then
# import the .pyd module.

from ctypes import WinDLL
import os

root = os.path.dirname(__file__)

WinDLL(os.path.join(root, "_libs/libgcc_s_sjlj-1-b97ee473.dll"))
WinDLL(os.path.join(root, "_libs/libwinpthread-1-177e075b.dll"))
WinDLL(os.path.join(root, "_libs/libwinpthread-1-6f6359c0.dll"))
WinDLL(os.path.join(root, "_libs/libgcc_s_seh-1-49206f22.dll"))
WinDLL(os.path.join(root, "_libs/libgcc_s_seh-1-58bff7ed.dll"))
WinDLL(os.path.join(root, "_libs/libquadmath-0-bfc9d31b.dll"))
WinDLL(os.path.join(root, "_libs/libquadmath-0-698a68e4.dll"))
WinDLL(os.path.join(root, "_libs/libgfortran-3-5869f77e.dll"))
WinDLL(os.path.join(root, "_libs/libblas-5228e251.dll"))
WinDLL(os.path.join(root, "_libs/liblapack-152834ea.dll"))
WinDLL(os.path.join(root, "_libs/vtkzlib-7.1-3b6207e8.dll"))
WinDLL(os.path.join(root, "_libs/vtkexpat-7.1-14123644.dll"))
WinDLL(os.path.join(root, "_libs/vtksys-7.1-caf4ca0d.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommoncore-7.1-bf02cb1b.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommonmisc-7.1-7c6d3e66.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommonmath-7.1-48a6df3c.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommonsystem-7.1-87ff2e19.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommontransforms-7.1-7ffe01c9.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommondatamodel-7.1-41be4195.dll"))
WinDLL(os.path.join(root, "_libs/vtkcommonexecutionmodel-7.1-f125c219.dll"))
WinDLL(os.path.join(root, "_libs/vtkiocore-7.1-e9f078e0.dll"))
WinDLL(os.path.join(root, "_libs/vtkioxmlparser-7.1-59002638.dll"))
WinDLL(os.path.join(root, "_libs/vtkioxml-7.1-d512957e.dll"))
WinDLL(os.path.join(root, "_libs/boost_python37-vc140-mt-x64-1_67-911f19b1.dll"))
WinDLL(os.path.join(root, "_libs/boost_numpy37-vc140-mt-x64-1_67-01121b10.dll"))
WinDLL(os.path.join(root, "_libs/blitzdg-4b0f63d1.dll"))
 
from .pyblitzdg import *

#missing gfortran
#and its deps (different versions of seh, and pthread)