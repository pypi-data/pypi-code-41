import numpy as np
import abc

from chainer_addons.dataset import AugmentationMixin
from chainer_addons.dataset import PreprocessMixin

from cvdatasets.dataset import AnnotationsReadMixin
from cvdatasets.dataset import RevealedPartMixin
from cvdatasets.dataset import IteratorMixin

class _pre_augmentation_mixin(abc.ABC):
	""" This mixin discards the parts from the ImageWrapper object
	and shifts the labels
	"""

	label_shift = 1

	def get_example(self, i):
		im_obj = super(_pre_augmentation_mixin, self).get_example(i)
		im, parts, lab = im_obj.as_tuple()
		return im, lab + self.label_shift

class _base_mixin(abc.ABC):
	""" This mixin converts images,that are in range
	[0..1] to the range [-1..1]
	"""

	def get_example(self, i):
		im, lab = super(_base_mixin, self).get_example(i)
		if isinstance(im, list):
			im = np.array(im)
		return im * 2 - 1, lab


class BaseDataset(_base_mixin,
	# augmentation and preprocessing
	AugmentationMixin, PreprocessMixin,
	_pre_augmentation_mixin,
	# random uniform region selection
	RevealedPartMixin,
	# reads image
	AnnotationsReadMixin,
	IteratorMixin):
	"""Commonly used dataset constellation"""
