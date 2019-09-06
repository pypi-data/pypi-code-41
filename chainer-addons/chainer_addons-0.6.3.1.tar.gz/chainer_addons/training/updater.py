from chainer.training import StandardUpdater

class MiniBatchUpdater(StandardUpdater):
	"""
		The iterator outputs batches in mini-batch sizes. This updater
		cummulates the gradients of these mini-batches until the
		batch_size is reached. Then a parameter update is performed
	"""
	def __init__(self, update_size=32, *args, **kwargs):
		super(MiniBatchUpdater, self).__init__(*args, **kwargs)
		self.update_size = update_size
		self.iteration_counter = 0

	def update_core(self):
		optimizer = self.get_optimizer('main')
		loss_func = self.loss_func or optimizer.target
		it = self.get_iterator('main')

		batch = it.next()
		data = self.converter(batch, self.device)

		use_cleargrads = getattr(optimizer, '_use_cleargrads', True)
		if use_cleargrads and self.iteration_counter == 0:
			optimizer.target.cleargrads()

		self.iteration_counter += it.batch_size
		loss = loss_func(*data)
		loss.backward()

		if self.iteration_counter >= self.update_size:
			self.iteration_counter = 0
			optimizer.update()
