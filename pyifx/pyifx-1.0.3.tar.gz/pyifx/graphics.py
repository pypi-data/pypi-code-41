import pyifx.INTERNAL as INTERNAL
import pyifx.misc as misc
import numpy as np

def blur_gaussian(img_paths, radius=3, size=None, write=True):
	"""blur_gaussian(img_paths, radius=3, size=None, write=True)
		Takes images(s) and blurs them using a gaussian kernel based on a given radius.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be blurred.

		:type radius: int
		:param radius: The radius of the gaussian kernel. If nothing is entered for this parameter, it will default to 3.

		:type size: list, NoneType
		:param size: The dimensions of the gaussian kernel. Must be entered in

		:type write: bool
		:param write: Whether to write the blurred image(s). 

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list

	"""
	INTERNAL._type_checker(radius, [int, float])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])
	INTERNAL._type_checker(size, [int, list, np.ndarray, None])

	return INTERNAL._convolution_handler(img_paths, radius=radius, type_kernel="gaussian", size=size, custom=None, write=write)

def blur_mean(img_paths, radius=3, write=True):
	""" blur_mean(img_paths, radius=3, write=True)
		Takes images(s) and blurs them using a mean kernel based on a given radius.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be blurred.

		:type radius: int
		:param radius: The radius of the mean kernel. If nothing is entered for this parameter, it will default to 3.

		:type write: bool
		:param write: Whether to write the blurred image(s). 

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""
	INTERNAL._type_checker(radius, [int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._convolution_handler(img_paths, radius=radius, type_kernel="mean", size=None, custom=None, write=write)

def pixelate(img_paths, factor=4, write=True):
	""" pixelate(img_paths, factor=4, write=True)
		Takes image(s) and pixelates them based on a given factor.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be pixelated.

		:type factor: int
		:param factor: How much the image(s) should be pixelated. If nothing is entered for this parameter, it will default to 4.

		:type write: bool
		:param write: Whether to write the pixelated image(s). 

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""
	INTERNAL._type_checker(factor, [int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._pixelate_handler(img_paths, factor, write=write)

def detect_edges(img_paths, write=True):
	""" detect_edges(img_paths, write=True)
		Takes image(s) and creates new images focusing on edges.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list 
		:param img_paths: The image(s) to be manipulated.

		:type write: bool
		:param write: Whether to write the manipulated image(s).

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list

	"""
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._detect_edges_handler(img_paths, write=write)

def convolute_custom(img_paths, kernel, write=True):
	""" convolute_custom(img_paths, kernel, write=True)
		Takes image(s) and creates new images that are convoluted over using a given kernel.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be convoluted over.

		:type kernel: numpy.ndarray, list 
		:param kernel: The kernel to be used for convolution. This can be provided in either a 2-dimensional list or a numpy 2-dimensional array.

		:type write: bool 
		:param write: Whether to write the convoluted image(s).

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
	"""
	INTERNAL._type_checker(kernel, [np.ndarray, list])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._convolution_handler(img_paths, radius=None, type_kernel=None, size=None, custom=kernel, write=write)