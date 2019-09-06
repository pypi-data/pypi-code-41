import abc
import numpy as np

from functools import partial

from chainer import cuda

class GammaMixin(abc.ABC):
	TWO_SQ_PI = np.sqrt(2 * np.pi)

	def __init__(self, eps):
		super(GammaMixin, self).__init__()
		self.eps = eps

	# @staticmethod
	# def expand_params(params, shape, xp=np):
	# 	bcast = partial(xp.broadcast_to, shape=shape)
	# 	return map(bcast, params)

	def _log_proba(self, x, mu, sigma, xp=np):
		assert x.ndim == 3, \
			"Number of dimensions of the input is not 3: {}!".format(x.ndim)

		n, t, in_size = x.shape
		_, n_components = mu.shape
		shape  = (n, t, in_size, n_components)

		_x = xp.broadcast_to(xp.expand_dims(x, -1), shape)
		_mu, _sig = [xp.broadcast_to(p, shape) for p in [mu, sigma]]

		_dist = (_x - _mu) / _sig
		return -xp.sum(_dist**2, axis=2) / 2, (_mu, _sig)

	def _proba(self, x, mu, sigma, w,
		weighted=True, return_params=False, xp=np):

		_log_proba, (_mu, _sig) = self._log_proba(x, mu, sigma, xp=xp)
		_proba = xp.exp(_log_proba)

		_w = xp.broadcast_to(w, _proba.shape)
		if weighted:
			_proba = xp.sum(_proba * _w, axis=-1)

		if return_params:
			return _proba, (_mu, _sig, _w)
		else:
			return _proba

	def _gamma(self, inputs, eps=None):
		xp = cuda.get_array_module(*inputs)

		x, mu, sigma, w = inputs
		n, t, in_size = x.shape
		_, n_components = mu.shape

		_log_proba, (_mu, _sig) = self._log_proba(x, mu, sigma, xp=xp)

		shape = (n, t, in_size, n_components)
		_x = xp.broadcast_to(xp.expand_dims(x, -1), shape)
		self._x_mu = _x - _mu
		self._sig = _sig

		_w = xp.broadcast_to(w, _log_proba.shape)
		self._log_wu = _log_proba + xp.log(_w)
		if xp == np:
			from scipy.special import logsumexp
			_log_wu_sum = logsumexp(self._log_wu, axis=-1, keepdims=True)
		else:
			import pdb; pdb.set_trace()

		# _wu_sum = xp.sum(self._wu, axis=-1, keepdims=True) #+ eps
		return xp.exp(self._log_wu - _log_wu_sum)

	def _gamma_grad(self, inputs, eps=None):
		eps = self.eps if eps is None else eps
		xp = cuda.get_array_module(*inputs)
		x, mu, sigma, w = inputs

		n, t, in_size = x.shape
		_, n_components = mu.shape

		_log_wu = xp.expand_dims(self._log_wu, axis=2)
		_log_x_mu_sig_2 = xp.log(self._x_mu) - 2 * xp.log(self._sig)

		_log_x_mu_sig_2[np.isnan(_log_x_mu_sig_2)] = 0

		if xp == np:
			from scipy.special import logsumexp
			_log_wu_sum = logsumexp(self._log_wu, axis=-1, keepdims=True)
			_log_wu_sum = xp.expand_dims(_log_wu_sum, axis=-1)
			_log_wu_sum = xp.broadcast_to(_log_wu_sum, _log_x_mu_sig_2.shape)
			# import pdb; pdb.set_trace()
			_log_g0 = _log_x_mu_sig_2 + _log_wu_sum

			_log_wu = xp.expand_dims(self._log_wu, axis=2)
			_log_wu = xp.broadcast_to(_log_wu, _log_x_mu_sig_2.shape)
			_log_g1 = logsumexp(_log_wu + _log_x_mu_sig_2, axis=-1, keepdims=True)

			# import pdb; pdb.set_trace()
			# sum_kwargs = dict(axis=3, keepdims=True)
			# g0 = _log_x_mu_sig_2
			# g1 = xp.sum(_wu * _x_mu_sig_2, **sum_kwargs) \
			# 	/ xp.sum(_wu, **sum_kwargs)

			return xp.exp(_log_g1) - xp.exp(_log_g0)
			res = np.log(res) - log
		else:
			import pdb; pdb.set_trace()


		return g0 + g1
