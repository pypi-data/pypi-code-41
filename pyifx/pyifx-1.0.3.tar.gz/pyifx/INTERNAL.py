import os
import sys
import numpy as np
import imageio
import math

def _check_path_type(path):
	if os.path.isdir(path):
		return 'dir'
	elif os.path.isfile(path):
		return 'file'
	else:
		return None









def _brightness_handler(img_paths, percent, method, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			if method == "b" or method == "d":
				new_vol.volume.append(_brightness_operation(img, percent, method, write=write))
			else:
				raise Exception("An internal error occurred.")

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
			if method == "b" or method == "d":
				return _brightness_operation(img_paths, percent, method, write=write)
			else:
				raise Exception("An internal error occurred.")

	elif type(img_paths) == list:
		new_imgs = []

		for img in img_paths:
			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")
			if method == "b" or method == "d":
				new_imgs.append(_brightness_operation(img, percent, method, write=write))
			else:
				raise Exception("Something went wrong.")
		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _brightness_operation(img, percent, method, write=True):
	import pyifx.misc as misc
	new_img = np.empty(shape=img.get_image().shape)

	for row in range(len(new_img)):
		for p in range(len(new_img[row])):
			for v in range(len(new_img[row][p])):
				value = img.get_image()[row][p][v]
				if method == "b":
					new_img[row][p][v] = min(255, value*(1+percent)-(value/6))
				elif method == "d":
					new_img[row][p][v] = max(0, value*(1-percent)+(value/6))
				else:
					raise Exception("An internal error occurred.")

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)

	if write:
		_write_file(new_img)

	return new_img




def _color_overlay_handler(img_paths, color, opacity, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:
		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_color_overlay_operation(img, color, opacity, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		return _color_overlay_operation(img_paths, color, opacity, write=write)

	elif type(img_paths) == list:
		new_imgs = []
		for img in img_paths:
			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_color_overlay_operation(img, color, opacity, write=write))
		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _color_overlay_operation(img, color, opacity, write=True):
	import pyifx.misc as misc
	new_img = np.empty(shape=img.get_image().shape)

	for row in range(len(new_img)):
		for p in range(len(new_img[row])):
			for v in range(len(new_img[row][p])):

				diff = (color[v]-img.get_image()[row][p][v])*opacity
				new_img[row][p][v] = min(255, max(img.get_image()[row][p][v]+diff, 0))

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)

	if write:
		_write_file(new_img)

	return new_img




def _saturation_handler(img_paths, percent, method, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			if method == "s" or method == "ds":
				new_vol.volume.append(_saturation_operation(img, percent, method, write=write))
			else:
				raise Exception("An internal error occurred.")

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		if method == "s" or method == "ds":
			return _saturation_operation(img_paths, percent, method, write=write)
		else:
			raise Exception("An internal error occurred.")

	elif type(img_paths) == list:
		new_imgs = []
		for img in img_paths:
			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")
			if method == "s" or method == "ds":
				new_imgs.append(_saturation_operation(img, percent, method, write=write))
			else:
				raise Exception("An internal error occurred.")
		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _saturation_operation(img, percent, method, write=True):
	import pyifx.misc as misc
	type_map = {"s": 1, "ds": -1}
	new_img = np.empty(shape=img.get_image().shape)

	for row in range(len(new_img)):
		for p in range(len(new_img[row])):

			gray_val = sum(img.get_image()[row][p])/3
			for v in range(len(new_img[row][p])):

				value = img.get_image()[row][p][v]
				diff = gray_val - value
				pixel_change = diff * (type_map[method]*percent)
				new_img[row][p][v] = max(0, min((img.get_image()[row][p][v]-pixel_change), 255))

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)
	if write:
		_write_file(new_img)
		
	return new_img








from pyifx import *

def _resize_handler(img_paths, new_size, write=True):
	import pyifx.misc as misc

	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_resize_operation(img, new_size, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		return _resize_operation(img_paths, new_size, write=write)

	elif type(img_paths) == list:
		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_resize_operation(img, new_size, write=write))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _resize_operation(img, new_size, write=True):
	import pyifx.misc as misc

	img_size = [int(d) for d in new_size.split('x')]
	if len(img_size) != 2:
		raise ValueError("Invalid value used: Invalid size entered. Please use the format: 'WxH'")

	img_size.append(3)
	img_size[0], img_size[1] = img_size[1], img_size[0]

	width_factor = img_size[1]/img.get_image().shape[1]
	height_factor = img_size[0]/img.get_image().shape[0]

	new_img = np.full(shape=img_size, fill_value=None)

	for r in range(len(new_img)):
		for p in range(len(new_img[r])):
			for c in range(len(new_img[r][p])):

				if new_img[r][p][c] != None:
						new_img[r][p][c] += img.get_image()[math.floor(r/height_factor)][math.floor(p/width_factor)][c]
						new_img[r][p][c] = math.floor(new_img[r][p][c]/2)
				else:
					new_img[r][p][c] = img.get_image()[math.floor(r/height_factor)][math.floor(p/width_factor)][c]

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)

	if write:
		_write_file(new_img)

	return new_img




def _change_file_type_handler(img_paths, new_type, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_change_file_type_operation(img, new_type, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		return _change_file_type_operation(img_paths, new_type, write=write)

	elif type(img_paths) == list:
		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_change_file_type_operation(img, new_type, write=write))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _change_file_type_operation(img, new_type, write=True):

	new_img = img
	accepted_types = ['.jpg', '.png', '.jpeg', 'jpg', 'jpeg', 'png']	
	if new_type.lower() not in accepted_types:
		raise ValueError("Invalid value used: New file type not in accepted file types.")

	if new_type[0] != '.':
		new_type = f".{new_type}"

	new_img.set_output_path(os.path.splitext(new_img.get_output_path())[0] + new_type)

	if write:
		_write_file(new_img)
	return new_img




def _rewrite_file_handler(img_paths):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_write_file(img_paths))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		return _write_file(img_paths)

	elif type(img_paths) == list:
		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_write_file(img))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")








def _convolution_handler(img_paths, radius, type_kernel, size, custom=None, write=True):
	import pyifx.misc as misc

	kernel = _create_kernel(radius, type_kernel, size, custom=custom)	

	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_convolution_operation(img, kernel, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:
		return _convolution_operation(img_paths, kernel, write=write)

	elif type(img_paths) == list:

		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_convolution_operation(img, kernel, write=write))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")	


def _convolution_operation(img, kernel, write=True):

	new_img = _convolute_over_image(img, kernel, write=False)

	if write:
		_write_file(new_img)

	return new_img


def _convolute_over_image(img, kernel, write=True):
	import pyifx.misc as misc

	new_img = np.empty(shape=img.get_image().shape)
	k_height = math.floor(kernel.shape[0]/2)
	k_width = math.floor(kernel.shape[1]/2)

	for r in range(len(img.get_image())):
		for p in range(len(img.get_image()[r])):
			for c in range(len(img.get_image()[r][p])):

				new_pixel_value = 0

				for row in range(-k_height, k_height+1):
					for column in range(-k_width, k_width+1):

						try:
							new_pixel_value += img.get_image()[r+column][p+row][c]*kernel[row+k_height][column+k_width]

						except IndexError:
							pass

				new_img[r][p][c] = min(255, max(0, new_pixel_value))	

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)

	if write:
		_write_file(new_img)

	return new_img




def _pixelate_handler(img_paths, factor, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_pixelate_operation(img, factor, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:

		return _pixelate_operation(img_paths, factor, write=write)

	elif type(img_paths) == list:

		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_pixelate_operation(img, factor, write=write))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _pixelate_operation(img, factor, write=True):
	import pyifx.misc as misc

	new_img = np.empty(shape=img.get_image().shape)

	for r in range(0, len(new_img)-factor, factor+1):
		for p in range(0, len(new_img[r])-factor, factor+1):

			value = img.get_image()[r][p]

			for row_fill in range(r, r+factor+1):
				for column_fill in range(p, p+factor+1):

					new_img[row_fill][column_fill] = value

	new_img = misc.PyifxImage(img.get_input_path(), img.get_output_path(), new_img, False)

	if write:
		_write_file(new_img)

	return new_img




def _detect_edges_handler(img_paths, write=True):
	import pyifx.misc as misc
	if type(img_paths) == misc.ImageVolume:

		if not os.path.exists(img_paths.get_output_path()):
			os.makedirs(img_paths.get_output_path())

		new_vol = misc.ImageVolume(img_paths.get_input_path(), img_paths.get_output_path(), img_paths.get_prefix(), img_paths.convert)
		new_vol.set_volume([])

		for img in img_paths.get_volume():
			new_vol.volume.append(_detect_edges_operation(img, write=write))

		return new_vol

	elif type(img_paths) == misc.PyifxImage:

		return _detect_edges_operation(img_paths, write=write)

	elif type(img_paths) == list:

		new_imgs = []

		for img in img_paths:

			if type(img) != misc.PyifxImage:
				raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")

			new_imgs.append(_detect_edges_operation(img, write=write))

		return new_imgs

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")


def _detect_edges_operation(img, write=True):
	import pyifx.misc as misc
	import pyifx.hsl as hsl

	x_dir_kernel = _create_kernel(None, "x-sobel", None)
	y_dir_kernel = _create_kernel(None, "y-sobel", None)

	x_dir_img = hsl.to_grayscale(_convolute_over_image(img, x_dir_kernel, write=False), write=False)
	y_dir_img = hsl.to_grayscale(_convolute_over_image(img, y_dir_kernel, write=False), write=False)

	edge_img = misc.combine(x_dir_img, y_dir_img, img.get_output_path(), write=False)
	edge_img.set_image(edge_img.get_image().astype(np.uint8))

	if write:
		_write_file(edge_img)
		
	return edge_img




def _create_kernel(radius, type_kernel, size, custom=None):

	if custom is not None:
		custom = np.array(custom)

		if len(custom.shape) != 2:
			raise ValueError("Invalid value used: Size of kernel must be 2-dimensional. Use the format (h,w) to achieve this.")

		for d in custom.shape:
			if d % 2 == 0:
				raise ValueError("Invalid value used: Kernel must have odd dimension sizes.")

		return custom

	if size != None:

		if len(size) != 2:
			raise ValueError("Invalid value used: Size of kernel must be 2-dimensional. Use the format (h,w) to achieve this.")

	kernel = None

	if type_kernel == "gaussian":

		if size == None:
			size = int(2*radius)
			if size % 2 == 0:
				size += 1

		if type(size) == int:
			size = [size, size]
		if type(size) == list:
			if len(size) != 2:
				raise ValueError("Invalid value used: Size either be in the format [W, H] or S (S -> [S,S]).")

		m,n = [(ss-1.)/2. for ss in size]
		y,x = np.ogrid[-m:m+1,-n:n+1]
		kernel = np.exp( -(x*x + y*y) / (2.*radius*radius) )
		kernel[ kernel < np.finfo(kernel.dtype).eps*kernel.max() ] = 0
		sumh = kernel.sum()
		if sumh != 0:
			kernel /= sumh

	elif type_kernel == "mean":
		if radius % 2 == 0:
			radius += 1
			
		divider = radius**2
		kernel = np.array([[1/divider for r in range(radius)] for h in range(radius)])

	elif type_kernel == "y-sobel":
		return np.array([[-1,-2,-1], [0,0,0], [1,2,1]])		

	elif type_kernel == "x-sobel":
		return np.array([[-1,0,1], [-2,0,2], [-1,0,1]])

	else:
		raise Exception("An internal error occurred.")

	kernel = np.flip(kernel, axis=1)

	return kernel


def _type_checker(var, types):

	for t in types:
		if t == None:
			if var == None:
				return True
		elif type(var) is t:
			return True

	raise TypeError("Invalid parameter type.")
	return False

def _write_file(img):
	out_path, extension = os.path.splitext(img.get_output_path())

	if not os.path.exists(os.path.split(img.get_output_path())[0]):
		os.makedirs(os.path.split(img.get_output_path())[0])

	file_count = 1
	temp_path = out_path

	while os.path.isfile(out_path + extension):
		out_path = temp_path
		out_path += f" ({file_count})"
		file_count += 1

	imageio.imwrite(out_path + extension, img.get_image().astype(np.uint8))
	return img

def _combine_handler(img1, img2, out_path, write=True):
	import pyifx.misc as misc

	old_imgs = [img1, img2]
	imgs = []

	for img in old_imgs:
		if type(img) == misc.PyifxImage:
			imgs.append(img)
		elif type(img) == misc.ImageVolume:
			imgs.append(img.get_volume())
		elif type(img) == list:
			for i in img:
				_type_checker(i, [misc.PyifxImage])
			imgs.append(img)

	if len(list(filter(lambda i: type(i) != list, imgs))) == 1:
		raise TypeError("Incorrect type used: Images must be a combination of types ImageVolume and list OR PyifxImage.")

	if (type(imgs[0]) == list and type(imgs[1]) == list):

		if len(imgs[0]) != len(imgs[1]):
			raise ValueError("Invalid value used: Lengths of image volumes and/or lists must be equal.")

		if not os.path.exists(os.path.split(out_path)[0]):
			os.makedirs(os.path.split(out_path)[0])

		new_imgs = []

		for i in range(len(imgs[0])):
			new_imgs.append(_combine_operation(imgs[0][i], imgs[1][i], out_path, write=write))

			return new_imgs

	elif type(imgs[0]) == misc.PyifxImage and type(imgs[1]) == misc.PyifxImage:

		return _combine_operation(imgs[0], imgs[1], out_path, write=write)

	else:
		raise TypeError("Invalid type used: Input contains non-Pyifx images and/or classes.")
	

def _combine_operation(img1, img2, out_path, write=True):
	import pyifx.misc as misc

	_type_checker(img1, [misc.PyifxImage])
	_type_checker(img2, [misc.PyifxImage])
	_type_checker(out_path, [str])

	if img1.get_image().shape[0]*img1.get_image().shape[0] <= img2.get_image().shape[0]*img2.get_image().shape[1]:
		shape = img1.get_image().shape
	else:
		shape = img2.get_image().shape

	new_img = np.empty(shape)

	for r in range(len(img1.get_image())):
		for p in range(len(img1.get_image()[r])):
			for c in range(len(img1.get_image()[r][p])):
				try:
					new_img[r][p][c] = min(255, max(0, (int(img1.get_image()[r][p][c])+int(img2.get_image()[r][p][c]))/2))

				except IndexError:
					pass

	img = misc.PyifxImage(None, out_path, new_img, False)

	if write:
		_write_file(img)

	return img