import os
import sys
import numpy as np
import imageio
import math
import pyifx.INTERNAL as INTERNAL

class PyifxImage():
	""" A class used to create packages of images & their properties created for use with the Pyifx library.
		
		:vartype input_path: str, NoneType
		:ivar input_path: The path to where the image is located. If the image does not have an input path, it means that the instance is a result of combining two or more images.

		:vartype output_path: str, NoneType 
		:ivar output_path: The path to where edited images should be created. If the image does not have an output path, it means the instance is used for read-only purposes.

		:vartype image: numpy.ndarray, NoneType
		:ivar image: The image located at the input path in the form of a numpy n-dimensional array. If the instance does not have an image property, it means that the image had not been read.

	"""

	def __init__(self, input_path, output_path=None, img=None, create_image=True):
		"""	__init__(self, path, output_path=None, img=None, create_image=True)
			The PyifxImage constructor method.

			:type path: str, NoneType
			:param path: The path to where the image is located. Only use None as a value if the image property of the instace is being specified.

			:type output_path: str, NoneType
			:param output_path: The path to where the edited image should be saved. Only use None as a value if the instance is not going to be saved to a file.

			:type img: numpy.ndarray, NoneType
			:param img: The data used for image editing & processing. The image property of the class will be set based on the input path unless this parameter is set to a value other than None.

			:type create_image: bool 
			:param create_image: Specify whether the image property should be read from the input path. If this is set to true, the image at the input path will override the specified image parameter.

			:return: PyifxImage instance 
			:rtype: pyifx.misc.PyifxImage

		"""
		INTERNAL._type_checker(input_path, [str, None])
		INTERNAL._type_checker(output_path, [str, None])
		INTERNAL._type_checker(img, [np.ndarray, None])
		INTERNAL._type_checker(create_image, [bool])

		self.input_path = input_path
		self.output_path = output_path
		self.image = img
		if create_image:
			self.image = np.asarray(imageio.imread(input_path))

	def refresh_image(self):
		"""	refresh_image(self):
			Re-reads image based on input path & overrides the current image property, then returns the instance.

			:return: PyifxImage instance 
			:rtype: pyifx.misc.PyifxImage

		"""
		self.image = np.asarray(imageio.imread(self.path))
		return self

	def get_input_path(self):
		""" get_input_path(self):
			Gets the instances input path and returns it.

			:return: Input path 
			:rtype: str

		"""
		return self.input_path

	def set_input_path(self, new_input_path):
		"""	set_input_path(self, new_input_path):
			Sets the instances input path and returns the instance.

			:type new_input_path: str
			:param new_input_path: What the input path will be set to.

			:return: PyifxImage instance
			:rtype: pyifx.misc.PyifxImage

		"""
		self.input_path = new_input_path
		self.refresh_image()
		return self

	def get_output_path(self):
		"""	get_output_path(self):
			Gets the instances output path and returns it.

			:return: Output path 
			:rtype: str

		"""
		return self.output_path

	def set_output_path(self, new_output_path):
		""" set_output_path(self, new_output_path):
			Sets the instances output path and returns the instance.

			:type new_output_path: str
			:param new_output_path: What the output path will be set to.

			:return: PyifxImage instance 
			:rtype: pyifx.misc.PyifxImage

		"""
		self.output_path = new_output_path
		return self

	def get_image(self):
		"""	get_image(self):
			Gets the instances image data and returns it.

			:return: Image data
			:rtype: numpy.ndarray

		"""
		return self.image

	def set_image(self, new_image):
		"""	set_image(self, new_image):
			Sets the instances image data and returns it.

			:type new_image: numpy.ndarray
			:param new_image: What the image property will be set to.

			:return: PyifxImage instance
			:rtype: pyifx.misc.PyifxImage

		"""
		self.image = new_image
		return self

	
class ImageVolume():
	"""A class used to import images from a directory into Python, creating a list of PyifxImage instances.

		:vartype input_path: str
		:ivar input_path: The path to the directory where the images are located.

		:vartype output_path: str
		:ivar output_path: The path where images in the volume should be saved.

		:vartype prefix: str
		:ivar prefix: The prefix for edited image file names.

		:vartype volume: list
		:ivar volume: The list of images imported from the input path.

	"""

	def __init__(self, input_path, output_path, prefix="_", convert=False):
		"""	__init__(self, input_path, output_path, prefix="_", convert=False)
			The ImageVolume constructor method.

			:type input_path: str
			:param input_path: The path to the directory where the images are located.

			:type output_path: str
			:param output_path: The path where images in the volume should be saved.

			:type prefix: str
			:param prefix: The prefix for edited image file names. If nothing is entered for this parameter, it will default to "_".

			:type convert: bool
			:param convert: Whether the instance should also read in images from subdirectories. If nothing is entered for this parameter, it will default to false.

			:return: ImageVolume instance
			:rtype: pyifx.misc.ImageVolume

		"""
		INTERNAL._type_checker(input_path, [str])
		INTERNAL._type_checker(output_path, [str])
		INTERNAL._type_checker(prefix, [str])
		INTERNAL._type_checker(convert, [bool])

		self.input_path = input_path
		self.output_path = output_path
		self.prefix = prefix
		self.convert = convert
		self.volume = self.volume_to_list(convert)

	def volume_to_list(self, convert=False):
		"""	volume_to_list(self, convert=False)
			The method used to create a list of PyifxImage instances based on the arguments entered in the constructor method. The volume property will be set based on the return value of this function.

			:type convert: bool
			:param convert: Whether to import images from subdirectories. If nothing is entered for this parameter, it will default to False.

			:return: PyifxImage list 
			:rtype: list

		"""

		INTERNAL._type_checker(self.get_input_path(), [str])
		INTERNAL._type_checker(self.get_output_path(), [str])
		INTERNAL._type_checker(self.get_prefix(), [str])
		
		return self.convert_dir_to_images(self.get_input_path(), convert)

	def get_input_path(self):
		"""	get_input_path(self):
			Gets the instances input path and returns it.

			:return: Input path 
			:rtype: str

		"""
		return self.input_path

	def set_input_path(self, new_input_path, convert=False):
		"""	set_input_path(self, new_input_path, convert=False):
			Sets the instances input path and returns it.

			:type new_input_path: str
			:param new_input_path: What the input path will be set to.

			:type convert: bool
			:param convert: Whether the instance should also read in images from subdirectories. If nothing is entered for this parameter, it will default to false.

			:return: ImageVolume instance 
			:rtype: pyifx.misc.ImageVolume

		"""
		self.input_path = new_input_path
		self.volume = self.volume_to_list(convert)
		return self

	def get_output_path(self):
		"""get_output_path(self):
			Gets the instances output path and returns it.

			:return: Output path 
			:rtype: str

		"""
		return self.output_path

	def set_output_path(self, new_output_path, convert=False):
		"""set_output_path(self, new_output_path):
			Sets the instances output path and returns the instance.

			:type new_output_path: str
			:param new_output_path: What the output path will be set to.

			:return: ImageVolume instance
			:rtype: pyifx.misc.ImageVolume

		"""
		self.output_path = new_output_path
		self.volume = self.volume_to_list(convert)
		return self

	def get_prefix(self):
		"""get_prefix(self):
			Gets the instances prefix property and returns it.

			:return: Prefix 
			:rtype: str

		"""
		return self.prefix

	def set_prefix(self, new_prefix):
		"""	set_prefix(self, new_prefix):
			Sets the instances prefix property and returns the instance.

			:type new_prefix: str
			:param new_prefix: What the instances prefix property will be set to.

			:return: ImageVolume instance 
			:rtype: pyifx.misc.ImageVolume

		"""
		self.prefix = new_prefix
		return self

	def get_volume(self):
		"""	get_volume(self):
			Gets the instances volume and returns it.

			:return: List of images of type PyifxImage OR An empty array 
			:rtype: list

		"""
		return self.volume

	def set_volume(self, new_volume):
		"""set_volume(self, new_volume):
			Sets the instances volume property and returns the volume.

			:type new_volume: list
			:param new_volume: What the instances volume will be set to.

			:return: ImageVolume instance 
			:rtype: pyifx.misc.ImageVolume

		"""
		if new_volume != []:
			for img in new_volume:
				INTERNAL._type_checker(img, [PyifxImage])
		self.volume = new_volume
		return self

	def convert_dir_to_images(self, input_dir, convert=False):
		"""	convert_dir_to_images(input_dir, convert=False):
			Converts files from a given directory into PyifxImage instances.
			
			:type input_dir: str
			:param input_dir: The directory to read files from.

			:type convert: bool
			:param convert: Whether to import images from subdirectories as well.

			:return: List with elements of type PyifxImage
			:rtype: list

		"""
		INTERNAL._type_checker(input_dir, [str])
	
		images = []
		possible_extensions = ['.jpg', '.jpeg', '.png']

		def add_to_images(internal_input_dir):
			for f in os.listdir(internal_input_dir):
			 	if os.path.splitext(f)[1] in possible_extensions:
			 		images.append(PyifxImage(internal_input_dir + f, os.path.join(self.get_output_path(),f"{self.get_prefix()}{os.path.split(f)[1]}")))

			 	if convert:
				 	if os.path.isdir(f):
				 		add_to_images(internal_input_dir + f)

		add_to_images(input_dir)
		return images


def combine(img1, img2, out_path, write=True):
	"""combine(img1, img2, out_path, write=True)
			Combines the data of two PyifxImages, ImageVolumes, or ImageLists to form new PyifxImages.

			:type img1: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
			:param img1: The first image to be added to the combination.

			:type img2: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list
			:param img2: The second image to be added to the combination. Arguments of type ImageVolume and list can be used in conjunction, but images of type PyifxImage must be used together.

			:type out_path: str
			:param out_path: The path that the combine image(s) will be written to.

			:type write: bool
			:param write: Whether to write the image or not.

			:return: PyifxImage instance, ImageVolume instance, or list with elements of type PyifxImage
			:rtype: pyifx.misc.PyifxImage, pyifx.misc.ImageVolume, list	

	"""

	INTERNAL._type_checker(img1, [PyifxImage, ImageVolume, list])
	INTERNAL._type_checker(img2, [PyifxImage, ImageVolume, list])
	INTERNAL._type_checker(out_path, [str])
	INTERNAL._type_checker(write, [bool])

	return INTERNAL._combine_handler(img1, img2, out_path, write=write)