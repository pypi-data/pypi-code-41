"""Jupyter configuration file

Note that the code in this file gets executed in a python process that is independent
of any python process in a kernel run by Jupyter (e.g., an ipython kernel). Thus we can make
changes to the installed packages to use in the ipython kernel here without worrying about
them not being reimported.
"""
from civis_jupyter_notebooks import notebook_config

c = get_config() # noqa
notebook_config.civis_setup(c)
