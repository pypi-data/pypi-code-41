from chainer.function import Function
from chainer import cuda

from .base import GammaMixin


class FVEncoding(Function, GammaMixin):

	def forward(self, inputs):
		xp = cuda.get_array_module(*inputs)

		x, mu, sigma, w = inputs
		n, t, in_size = x.shape
		_, n_components = mu.shape

		_gamma = self._gamma(inputs)

		self.gamma = xp.broadcast_to(
			xp.expand_dims(_gamma, axis=2), self._x_mu.shape)

		_x_mu_sig = self._x_mu / self._sig

		G_mu = xp.sum(self.gamma * _x_mu_sig, axis=1)
		G_sig = xp.sum(self.gamma * (_x_mu_sig**2 - 1), axis=1)

		_w = xp.broadcast_to(w, (n, in_size, n_components))

		G_mu /= n_components * xp.sqrt(_w)
		G_sig /= n_components * xp.sqrt(2 * _w)

		# 2 * (n, in_size, n_components) -> (n, in_size, n_components, 2) -> (n, 2*in_size*n_components)
		res = xp.stack([G_mu, G_sig], axis=-1).reshape(n, -1)
		# res = xp.stack([G_mu], axis=-1).reshape(n, -1)
		return res,


	def backward(self, inputs, gys):
		xp = cuda.get_array_module(*inputs)
		x, mu, sigma, w = inputs

		n, t, in_size = x.shape
		_, n_components = mu.shape

		# ##### gamma-Gradient computation #####
		g_gamma = self._gamma_grad(inputs)

		##### G_mu- and G_sig-Gradient computation #####
		_x_mu, _sig = self._x_mu, self._sig

		shape = (n, t, in_size, n_components)
		_w = xp.broadcast_to(w[None][None][None], shape)
		g_G_mu  = self.gamma * (g_gamma * _x_mu + 1) / (n_components * xp.sqrt(_w) * _sig)

		g_G_sig = self.gamma * (
				g_gamma * (_x_mu**2 / _sig**2 - 1) + \
				2 * _x_mu / _sig**2
			) / (n_components * xp.sqrt(_w * 2))

		##### reshaping according to the output gradients #####
		gx = xp.stack([g_G_mu, g_G_sig], axis=-1)
		# gx = xp.stack([g_G_mu], axis=-1)
		_gy = xp.reshape(gys[0], (n, in_size, n_components, gx.shape[-1]))
		_gy = xp.expand_dims(_gy, axis=1)
		gx = xp.sum(gx * _gy, axis=(-1, -2))

		grads = gx, None, None, None
		return grads

def fv_encoding(x, mu, sigma, w, eps=None):
	return FVEncoding(eps=eps)(x, mu, sigma, w)
