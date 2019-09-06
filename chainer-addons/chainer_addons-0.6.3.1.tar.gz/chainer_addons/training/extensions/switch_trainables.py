from chainer.training import Extension
from chainer.training import trigger as trigger_module


class SwitchTrainables(Extension):

	def __init__(self, switch_epochs, model, pooling):
		self.switch_epochs = switch_epochs
		self._trigger = trigger_module.get_trigger((switch_epochs, "epoch"))

		self.model = model
		self.pooling = pooling

	def __call__(self, trainer):
		if not self._trigger(trainer): return

		epoch = trainer.updater.epoch

		if (epoch / self.switch_epochs) % 2 == 0:
			self.model.enable_update()
			self.pooling.disable_update()
		else:
			self.model.disable_update()
			self.pooling.enable_update()

	def initialize(self, trainer):
		self.pooling.disable_update()

