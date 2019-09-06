from chainer.function import Function
from chainer import cuda

from .base import GammaMixin

class Gamma(Function, GammaMixin):

	def forward(self, inputs):
		self.y = self._gamma(inputs)
		return self.y,

	def backward(self, inputs, gys):
		xp = cuda.get_array_module(*inputs)

		g_gamma = self._gamma_grad(inputs)

		y = xp.broadcast_to(xp.expand_dims(self.y, axis=2), self._x_mu.shape)
		gy = xp.broadcast_to(xp.expand_dims(gys[0], axis=2), self._x_mu.shape)

		gx = (gy * g_gamma * y).sum(axis=3)
		return gx, None, None, None

def gamma(x, mu, sig, w, eps=None):
	return Gamma(eps=eps)(x, mu, sig, w)
