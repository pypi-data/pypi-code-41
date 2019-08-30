import sys
import os
import platform
import ctypes
import glob

if sys.platform in {"linux", "linux2"}:
    # Must be loaded in order:
    # libstdc++.so: copied from ubuntu 18.04
    # libdepthengine.so*: copied from K4A installation on ubuntu 18.04
    # libk4a.so*: build on ubuntu 16.04
    # libk4arecord.so*: build on ubuntu 16.04
    print("Loadng shared libs for Open3D with K4A on Ubuntu 16.04...")
    print("This is an unofficial fix. Use it at your own risk.")

    dll_files = [
        "libstdc++.so*", "libdepthengine.so*", "libk4a.so*", "libk4arecord.so*"
    ]
    pwd = os.path.dirname(os.path.realpath(__file__))

    for dll_file in dll_files:
        full_paths = glob.glob(pwd + "/" + dll_file)
        if len(full_paths) != 1:
            raise RuntimeError("Not found or more than one libs found for",
                               dll_file)
        else:
            ctypes.cdll.LoadLibrary(full_paths[0])
            print("Python loaded {}".format(dll_file))

    # The Open3D C++ mudule may check LD_LIBRARY_PATH to load
    # "libk4a.so*", "libk4arecord.so*"
    os.environ['LD_LIBRARY_PATH'] = pwd + ":" + os.environ['LD_LIBRARY_PATH']
else:
    raise RuntimeError(
        "Only supports Ubuntu 16.04. {} is unsupported".format(sys.platform))
