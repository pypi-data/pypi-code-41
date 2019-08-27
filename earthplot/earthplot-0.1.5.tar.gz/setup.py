# -*- coding: utf-8 -*-
"pyloco task setup script"

if __name__ == "__main__":

    from setuptools import setup, find_packages

    __taskname__ = "earthplot"

    setup(
        name="earthplot",
        version="0.1.5",
        packages=find_packages(),
        package_data={},
        install_requires=["ncplot", "cartopy", "pyloco>=0.0.134", "Cartopy>=0.17.0"],
        entry_points = {"pyloco.task": ["{taskname} = {taskname}:entry_task".format(taskname=__taskname__)]},
    )
