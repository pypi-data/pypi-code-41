import numpy as np

from unittest import TestCase

import chainer
import chainer.functions as F

from chainer_addons.links.fisher_encoding import FVLayer
from cyvlfeat.fisher import fisher
from cyvlfeat.gmm import gmm, cygmm

from .base import BaseFVEncodingTest

class FVLayerTest(BaseFVEncodingTest):

	def _new_layer(self, *args, **kwargs):
		return super(FVLayerTest, self)._new_layer(layer_cls=FVLayer)

	def test_output_shape(self):
		layer = self._new_layer()

		with chainer.using_config("train", False):
			output = layer(self.X)

		output_shape = (self.n, 2 * self.n_components * self.in_size)
		self.assertEqual(output.shape, output_shape,
			"Output shape was not correct!")

	def test_output(self):
		layer = self._new_layer()

		mean, var, w = (layer.mu, layer.sig, layer.w)

		with chainer.using_config("train", False):
			output = layer(self.X).array

		x = self.X.array.astype(np.float32)

		# we need to convert the array in Fortran order, but still remain the dimensions,
		# since the python API awaits <dimensions>x<components> arrays,
		# but they are indexed with "i_cl*dimension + dim" in the C-Code

		params = (
			mean.ravel(order="F").reshape(mean.shape, order="C").copy(),
			var.ravel(order="F").reshape(var.shape, order="C").copy(),
			w.copy(),
		)
		ref = [fisher(_x.T, *params,
					normalized=False,
					square_root=False,
					improved=False,
					fast=False,
					verbose=False,
			) for _x in x]

		ref = np.stack(ref)

		self.assertEqual(output.shape, ref.shape,
			"Output shape was not equal to ref shape!")

		self.assertClose(output, ref,
			"Output was not similar to reference")


	def test_cygmm(self):
		layer = self._new_layer()
		params = mean, var, w = (layer.mu, layer.sig, layer.w)

		x = self.X.array.astype(np.float32)
		gamma = layer.soft_assignment(x).array
		log_proba, _ = layer.log_proba(x, weighted=True)
		log_proba = log_proba.array

		for i, _x in enumerate(x):
			cy_mean, cy_var, cy_w, LL, cy_gamma = cygmm.cy_gmm(
				_x,
				self.n_components,
				0, # max_iterations
				"custom".encode("utf8"), # init_mode
				1, # n_repitions
				0, # verbose
				covariance_bound=None,

				init_means=mean.T.copy(),
				init_covars=var.T.copy(),
				init_priors=w.copy(),
			)

			self.assertClose(gamma[i], cy_gamma,
				f"[{i}] Soft assignment was not similar to reference (vlfeat)")

			self.assertClose(float(log_proba[i].sum()), LL,
				f"[{i}] Log-likelihood was not similar to reference (vlfeat)")
