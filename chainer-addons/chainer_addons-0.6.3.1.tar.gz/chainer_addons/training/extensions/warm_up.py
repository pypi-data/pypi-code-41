from chainer.training import Extension
from chainer.training import trigger as trigger_module


class WarmUp(Extension):

	def __init__(self, epochs, model, initial_lr, warm_up_lr=1.0):
		super(WarmUp, self).__init__()
		self.epochs = epochs
		self._trigger = trigger_module.get_trigger((epochs, "epoch"))

		self.lr = initial_lr
		self.warm_up_lr = warm_up_lr
		self.model = model
		assert hasattr(self.model, "clf_layer"), \
			"Model instance should have \"clf_layer\" attribute!"

		self._done = False

	def initialize(self, trainer):
		self.model.disable_update()
		self.model.clf_layer.enable_update()

		opt = trainer.updater.get_optimizer("main")
		if hasattr(opt, "alpha"):
			opt.alpha = self.warm_up_lr
		else:
			opt.lr = self.warm_up_lr

	def __call__(self, trainer):
		if not self._trigger(trainer): return
		if self._done: return

		opt = trainer.updater.get_optimizer("main")
		if hasattr(opt, "alpha"):
			opt.alpha = self.lr
		else:
			opt.lr = self.lr

		self.model.enable_update()
		self._done = True
