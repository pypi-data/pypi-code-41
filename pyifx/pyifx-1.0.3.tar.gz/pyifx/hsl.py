import pyifx.INTERNAL as INTERNAL
import pyifx.misc as misc

def brighten(img_paths,percent=45, write=True):
	""" brighten(img_paths, percent=45, write=True)
		Takes image(s) and brightens them.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be brightened.

		:type percent: int 
		:param percent: How much the image(s) should be brightened. If nothing is entered for this parameter, it will default to 45. The parameter must be between 0 and 100 (inclusive).

		:type write: bool 
		:param write: Whether to write the brightened image(s).					

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""
	INTERNAL._type_checker(percent, [float, int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	if percent < 0 or percent > 100:
		raise ValueError("Invalid value used: percentage must be between 0 and 100.")

	return INTERNAL._brightness_handler(img_paths, percent/100, "b", write=write)


def darken(img_paths,percent=45, write=True):
	""" darken(img_paths, percent=45, write=True)
		Takes image(s) and darkens them.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list 
		:param img_paths: The image(s) to be darkened.

		:type percent: int 
		:param percent: How much the image(s) should be darkened. If nothing is entered for this parameter, it will default to 45. The parameter must be between 0 and 100 (inclusive).

		:type write: bool 
		:param write: Whether to write the darkened image(s).					

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""	
	INTERNAL._type_checker(percent, [float, int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	if percent < 0 or percent > 100:
		raise ValueError("Invalid value used: percentage must be between 0 and 100.")

	return INTERNAL._brightness_handler(img_paths, percent/100, "d", write=write)


def color_overlay(img_paths, color, opacity=30, write=True):
	""" color_overlay(img_paths, color, opacity=30, write=True)
		Takes image(s) and applies a specified color over it/them.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list 
		:param img_paths: The image(s) to be manipulated.

		:type color: numpy.ndarray, list
		:param color: The color to be applied over the image(s). This parameter should be specified in the format [Red, Green, Blue], with each component being between 0 and 255 (inclusive).

		:type opacity: int 
		:param opacity: How visible the color should be. If nothing is entered for this parameter, it will default to 30. It should be between 0 and 100 (inclusive).

		:type write: bool
		:param write: Whether to write the darkened image(s).

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list

	"""	

	INTERNAL._type_checker(opacity, [float, int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	if len(color) != 3:
		raise ValueError("Invalid value used: Please enter a color using the following format: [R,G,B].")

	for channel in color:
		INTERNAL._type_checker(channel, [int])
		if channel < 0 or channel > 255:
			raise ValueError("Invalid value used: Color channels must be between 0 and 255.")

	if opacity < 0 or opacity > 100:
		raise ValueError("Invalid value used: opacity must be between 0 and 100.")	

	return INTERNAL._color_overlay_handler(img_paths, color, opacity/100, write=write)


def saturate(img_paths, percent=30, write=True):
	""" saturate(img_paths, percent=30, write=True)
		Takes image(s) and saturates them.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be saturated.

		:type percent: int
		:param percent: How much the image(s) should be saturated. If nothing is entered for this parameter, it will default to 30. The parameter must be between 0 and 100 (inclusive).

		:type write: bool 
		:param write: Whether to write the saturated image(s).					

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""

	INTERNAL._type_checker(percent, [float, int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	if percent < 0:
		raise ValueError("Invalid value used: percentage must be greater than 0.")

	return INTERNAL._saturation_handler(img_paths, percent/100, "s", write=write)


def desaturate(img_paths, percent=30, write=True):
	""" desaturate(img_paths, percent=30, write=True)
		Takes image(s) and desaturates them.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list 
		:param img_paths: The image(s) to be desaturated.

		:type percent: int
		:param percent: How much the image(s) should be desaturated. If nothing is entered for this parameter, it will default to 30. The parameter must be between 0 and 100 (inclusive).

		:type write: bool
		:param write: Whether to write the desaturated image(s).

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list

	"""

	INTERNAL._type_checker(percent, [float, int])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	if percent < 0 or percent > 100:
		raise ValueError("Invalid value used: percentage must be between 0 and 100.")

	return INTERNAL._saturation_handler(img_paths, percent/100, "ds", write=write)


def to_grayscale(img_paths, write=True):
	""" to_grayscale(img_paths, write=True)
		Takes image(s) and converts them to grayscale.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be converted.

		:type write: bool
		:param write: Whether to write the grayscale image(s).					

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list

	"""
	
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._saturation_handler(img_paths, 1, "ds", write=write)