
import os
import trimesh

from tkinter import Tk
from tkinter.filedialog import askopenfilename

from PySimultan.vertice import *
from PySimultan.edge import *
from PySimultan.edge_loop import *
from PySimultan.face import *
from PySimultan.building import *
from PySimultan.material import *

# mesh = trimesh.load('../models/featuretype.STL')


def import_stl(file=None):
    mesh = trimesh.load(file)
    pass


if __name__ == '__main__':

    # file picker for debugging surposes
    Tk().withdraw()
    file = askopenfilename()

    MyBuilding = import_stl(file)

    print('done')