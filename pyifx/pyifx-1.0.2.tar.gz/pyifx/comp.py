import pyifx.INTERNAL as INTERNAL
import pyifx.misc as misc

def resize(img_paths, new_size, write=True):
	""" resize(img_paths, new_size, write=True)
		Takes image(s) and converts them to a given size.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be resized.

		:type new_size: str
		:param new_size: The new size to convert the image(s) to. It must be entered in the form "WidthxHeight".

		:type write: bool
		:param write: Whether to write the resized image(s). 

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	
			
	"""
	INTERNAL._type_checker(write, [bool])
	INTERNAL._type_checker(new_size, [str])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])

	return INTERNAL._resize_handler(img_paths, new_size, write)

def change_file_type(img_paths, new_type, write=True):
	""" change_file_type(img_paths, new_type, write=True)
		Takes image(s) and converts them to a given file type.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be converted.

		:type new_type: str
		:param new_type: The file type that the image(s) should be converted to. Available types: PNG, JPG, JPEG. Can be entered with/without the dot. Parameter is case-insensitive.

		:type write: bool
		:param write: Whether to write the converted image(s). 

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""
	INTERNAL._type_checker(write, [bool])
	INTERNAL._type_checker(new_type, [str])
	INTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])

	return INTERNAL._change_file_type_handler(img_paths, new_type, write=write)

def rewrite_file(img_paths):
	""" rewrite_file(img_paths)
		Takes image(s) and writes them to an output destination based on their properties. Intended for use with changes to pyifx class instances.

		:type img_paths: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
		:param img_paths: The image(s) to be rewritten.

		:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
		:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list			

	"""
	NTERNAL._type_checker(img_paths, [misc.PyifxImage, misc.ImageVolume, list])

	return INTERNAL._rewrite_file_handler(img_paths)
