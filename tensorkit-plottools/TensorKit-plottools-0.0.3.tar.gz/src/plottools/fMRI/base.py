import numpy as np
import h5py
from pathlib import Path
import matplotlib.colors as mcolors
from scipy.io import loadmat

maryland_cmap = mcolors.LinearSegmentedColormap.from_list(
    "RedBlue",
    [
        (0, 242 / 256, 255 / 256),
        (0, 123 / 256, 255 / 256),
        (0, 0, 1.0),
        (0, 0, 0),
        (1.0, 0, 0),
        (255 / 256, 89 / 256, 0),
        (255 / 256, 229 / 256, 0),
    ],
)


def _insert_masked_voxeldata_f_order(img, mask, voxeldata):
    # For some reason img[mask == 1] = voxeldata.T is not working
    # This is probably related to some backend memory weirdness
    # within numpy...
    img.T[mask.T == 1] = voxeldata
    return img


def get_fMRI_image(voxeldata, mask):
    """Places the 1D voxeldata into the correct voxels from a 3D mask.

    Arguments
    ---------
    voxeldata : np.ndarray
        1D array containing the voxeldata
    mask : np.ndarray
        3D array containing a boolean mask of which voxels the voxeldata
        is extracted from
    """
    img = np.zeros_like(mask, dtype=np.float)
    img = _insert_masked_voxeldata_f_order(img, mask, voxeldata)
    return np.ma.masked_array(img, mask=mask == 0)

def _get_fmri_images_from_unfolded(voxeldata, mask):
    # voxeldata along mode 0
    assert len(voxeldata.shape) == 2
    voxeldata = np.ascontiguousarray(voxeldata.T)
    images = []

    for i, _ in enumerate(voxeldata):
        images.append(get_fMRI_image(voxeldata[i], mask))
    
    images = np.ma.stack(images, axis=-1)

    return images

def get_fMRI_images(voxeldata, mask, axis=0):
    assert len(voxeldata.shape) < 4
    if axis == 1:
        voxeldata = np.moveaxis(voxeldata, 1, 0)
        return np.moveaxis(get_fMRI_images(voxeldata, mask, 0), 1, 0)
    elif axis == 2:
        voxeldata = voxeldata.transpose(2, 0, 1)
        output = get_fMRI_images(voxeldata, mask, 0)
        return output.transpose(1, 2, 0)
    elif axis == 0:
        vshape = voxeldata.shape
        voxeldata_unfolded = np.ascontiguousarray(voxeldata).reshape(vshape[0], -1)
        output = _get_fmri_images_from_unfolded(voxeldata_unfolded, mask)
        return output.reshape((*mask.shape, *vshape[1:]))
    else:
        raise ValueError('Axis must be 0, 1, or 2.')

def load_template(path=None):
    """Load template image"""
    if path is None:
        path = Path(__file__).parent / "fmri_template.h5"

    with h5py.File(path) as h5:
        template = h5["template"][...]

    return template


def load_mask(path, varname="mask"):
    return load_matlab_variable(path, varname)


def load_matlab_variable(path, varname):
    return (loadmat(path, variable_names=varname))[varname]


def tile_image(imgs, num_rows, num_cols):
    h, w, num_imgs = imgs.shape
    tiled_img = np.zeros([h * num_rows, w * num_cols])

    for i in range(num_rows):
        for j in range(num_cols):
            if (j + (i * num_cols)) > num_imgs:
                break
            tiled_img[i * h : (i + 1) * h, j * w : (j + 1) * w] = imgs[
                ..., (j + (i * num_cols))
            ]

    return tiled_img


class MatfileWrapper:
    def __init__(self, matfile, varname="fALFF", filenames=None):
        self.matfile = matfile
        self.varname = varname
        self.filenames = None
        with h5py.File(matfile) as h5:
            self.num_patients = h5[varname].shape[0]
            self.num_timesteps = h5[varname].shape[-1]
            if filenames is not None:
                _filenames = [h5[data[0]][...] for data in h5[filenames]]
                self.filenames = [
                    "".join((map(chr, np.squeeze(filename)))) for filename in _filenames
                ]

    def load_all_patients(self):
        with h5py.File(self.matfile) as h5:
            return h5[self.varname][...]

    def iterate_patients(self):
        with self:
            for patid in range(self.num_patients):
                yield self._h5[self.varname][patid]
        return

    def iterate_timesteps(self):
        with self:
            for timestep in range(self.num_timesteps):
                yield self._h5[self.varname][..., timestep]

    def __enter__(self):
        if self.entered:
            return self
        self.entered = True
        self._h5 = h5py.File(self.matfile)

    def __exit__(self, exctype, value, tb):
        if exctype is GeneratorExit:
            return False
        self._h5.close()
        self.entered = False
        return True
