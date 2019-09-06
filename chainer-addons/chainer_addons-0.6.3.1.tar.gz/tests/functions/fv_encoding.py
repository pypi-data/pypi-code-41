import numpy as np

from unittest import TestCase, skip

import chainer
import chainer.functions as F

from chainer_addons.links.fisher_encoding import FVLayer
from chainer_addons.functions import fv_encoding, gamma

class BaseTestCase(TestCase):

	def __init__(self, *args, **kwargs):
		super(BaseTestCase, self).__init__(*args, **kwargs)
		self.xp = np

		self.n, self.t, self.in_size = 2, 3, 512
		self.n_components = 3
		self.eps = 0#1e-12

		self.seed = 8934567
		self.dtype = np.float32

	def setUp(self):
		rnd = self.xp.random.RandomState(self.seed)

		X = rnd.randn(self.n, self.t, self.in_size).astype(self.dtype)
		self.X0 = chainer.Variable(X)
		self.X1 = chainer.Variable(X)

		self.init_mu = rnd.randn(self.in_size, self.n_components).astype(self.dtype)
		# self.init_mu = self.xp.ones((self.in_size, self.n_components), self.dtype)

	def _new_fv_layer(self, init_mu=None, init_sig=1):
		return FVLayer(
			self.in_size,
			self.n_components,
			init_mu=self.init_mu if init_mu is None else init_mu,
			init_sig=init_sig,
			eps=self.eps)

class GammaFunctionTest(BaseTestCase):

	def setUp(self):
		super(GammaFunctionTest, self).setUp()

		layer = self._new_fv_layer()

		self.mu = layer.mu
		self.sig = layer.sig
		self.w = layer.w

	def _expand_params(self, params, shape):
		_f = lambda param: \
			F.broadcast_to(
				F.expand_dims(
					F.expand_dims(param, axis=0), axis=0), shape)
		return map(_f, params)

	def _log_proba(self, x, mu, sig):
		shape = (self.n, self.t, self.in_size, self.n_components)

		_x = F.broadcast_to(F.expand_dims(x, -1), shape)
		_mu, _sig = self._expand_params([mu, sig], shape)
		x_mu = F.expand_dims(F.transpose(_x - _mu), axis=1)

		_dist = (_x - _mu) / _sig
		_dist = F.sum(_dist**2, axis=2)
		return -_dist / 2

	def _proba(self, x, mu, sig):
		return F.exp(self._log_proba(x, mu, sig))

	def _reference_gamma(self, x, mu, sig, w):

		_log_proba = self._log_proba(x, mu, sig)
		# self._proba = _proba.array
		_w = F.broadcast_to(F.expand_dims(w, axis=0), _log_proba.shape)
		_log_wu =  _log_proba + F.log(_w)

		_log_wu_sum = F.logsumexp(_log_wu, axis=-1)
		_log_wu_sum = F.expand_dims(_log_wu_sum, -1)
		_log_wu_sum = F.broadcast_to(_log_wu_sum, _log_wu.shape)

		return F.exp(_log_wu - _log_wu_sum)

	def test_gamma_outputs(self):

		gamma0 = self._reference_gamma(self.X0, self.mu, self.sig, self.w)
		gamma1 = gamma(self.X1, self.mu, self.sig, self.w, eps=self.eps)

		self.assertTrue(np.allclose(gamma0.array, gamma1.array),
			"Both implementations should have similar result, but was:\n"+\
			f"{gamma0.array}\n~=\n{gamma1.array}")


		self.assertTrue(np.all(gamma0.array == gamma1.array),
			"Both implementations should have the same result, but was:\n"+\
			f"{gamma0.array}\n!=\n{gamma1.array}")

	@skip
	def test_gamma_gradients(self):

		gamma0 = self._reference_gamma(self.X0, self.mu, self.sig, self.w)
		gamma1 = gamma(self.X1, self.mu, self.sig, self.w, eps=self.eps)

		self.X0.grad, self.X1.grad = None, None

		F.sum(gamma0).backward()
		F.sum(gamma1).backward()

		self.assertIsNotNone(self.X0.grad,
			"Gradient of X0 was not computed!")

		self.assertIsNotNone(self.X1.grad,
			"Gradient of X1 was not computed!")
		# import pdb; pdb.set_trace()

		self.assertTrue(np.allclose(self.X0.grad, self.X1.grad, atol=1e-7),
			"Both computed gradients should be similar, but were:\n" + \
			f"{self.X1.grad}\n~=\n{self.X0.grad}")

		self.assertTrue(np.all(self.X0.grad==self.X1.grad),
			"Both computed gradients should be equal, but were:\n" + \
			f"{self.X0.grad}\n!=\n{self.X1.grad}")

class FVFunctionTests(BaseTestCase):

	def setUp(self):
		super(FVFunctionTests, self).setUp()

		self.layer0 = self._new_fv_layer()
		self.layer1 = self._new_fv_layer()

	def test_layer_mus(self):
		self.assertTrue(np.all(self.layer0.mu == self.layer1.mu),
			"mus should be initialized equally!")

	@skip
	def test_fv_encoding_outputs(self):
		y0 = self.layer0(self.X0)

		mu, sigma, w = self.layer1.mu, self.layer1.sig, self.layer1.w
		y1 = fv_encoding(self.X1, mu, sigma, w, eps=self.eps)

		self.assertTrue(np.allclose(y0.array, y1.array),
			"Both implementations should have similar result, but were:\n"+\
			f"{y0.array}\n~=\n{y1.array}")

		self.assertTrue(np.all(y0.array == y1.array),
			"Both implementations should have the same result, but were:\n"+\
			f"{y0.array}\n!=\n{y1.array}")

	@skip
	def test_fv_encoding_gradients(self):

		y0 = self.layer0(self.X0)

		mu, sigma, w = self.layer1.mu, self.layer1.sig, self.layer1.w
		y1 = fv_encoding(self.X1, mu, sigma, w, eps=self.eps)

		self.X0.grad, self.X1.grad = None, None

		F.sum(y0).backward()
		F.sum(y1).backward()

		self.assertIsNotNone(self.X0.grad,
			"Gradient of X0 was not computed!")

		self.assertIsNotNone(self.X1.grad,
			"Gradient of X1 was not computed!")

		self.assertTrue(np.allclose(self.X0.grad, self.X1.grad, atol=1e-7),
			"Both computed gradients should be similar, but were:\n" + \
			f"{self.X1.grad}\n~=\n{self.X0.grad}")

		self.assertTrue(np.all(self.X0.grad==self.X1.grad),
			"Both computed gradients should be equal, but were:\n" + \
			f"{self.X1.grad}\n!=\n{self.X0.grad}")

