import chainer
import chainer.functions as F
import numpy as np

import abc
import logging

from chainer.backends import cuda
from chainer.optimizer_hooks import Lasso
from chainer.optimizer_hooks import WeightDecay
from chainer.training import StandardUpdater, extensions
from chainer.serializers import save_npz

from chainer_addons.models import ModelType
from chainer_addons.models import Classifier
from chainer_addons.models import PrepareType
from chainer_addons.training import optimizer, optimizer_hooks
from chainer_addons.functions import smoothed_cross_entropy

from cvdatasets.annotations import AnnotationType
from cvdatasets.utils import new_iterator

from functools import partial
from os.path import join

from bdb import BdbQuit


def check_param_for_decay(param):
	return param.name != "alpha"


def _format_kwargs(kwargs):
	return " ".join([f"{key}={value}" for key, value in kwargs.items()])

class _ModelMixin(abc.ABC):
	"""This mixin is responsible for optimizer creation, model creation,
	model wrapping around a classifier and model weights loading.
	"""

	def __init__(self, classifier_cls, classifier_kwargs={}, model_kwargs={}, *args, **kwargs):
		super(_ModelMixin, self).__init__(*args, **kwargs)
		self.classifier_cls = classifier_cls
		self.classifier_kwargs = classifier_kwargs
		self.model_kwargs = model_kwargs

	def wrap_model(self, opts):

		clf_class, kwargs = self.classifier_cls, self.classifier_kwargs

		self.clf = clf_class(
			model=self.model,
			loss_func=self._loss_func(opts),
			**kwargs)

		logging.info(" ".join([
			f"Wrapped the model around {clf_class.__name__}",
			f"with kwargs: {_format_kwargs(kwargs)}",
		]))

	def _loss_func(self, opts):
		if opts.l1_loss:
			return F.hinge

		elif opts.label_smoothing >= 0:
			assert opts.label_smoothing < 1, \
				"Label smoothing factor must be less than 1!"
			return partial(smoothed_cross_entropy,
				N=self.n_classes,
				eps=opts.label_smoothing)
		else:
			return F.softmax_cross_entropy

	def init_optimizer(self, opts):
		"""Creates an optimizer for the classifier """

		opt_kwargs = {}
		if opts.optimizer == "rmsprop":
			opt_kwargs["alpha"] = 0.9

		self.opt = optimizer(opts.optimizer,
			self.clf,
			opts.learning_rate,
			decay=0, gradient_clipping=False, **opt_kwargs
		)

		if opts.decay:
			reg_kwargs = {}
			if opts.l1_loss:
				reg_cls = Lasso

			elif opts.pooling == "alpha":
				reg_cls = optimizer_hooks.SelectiveWeightDecay
				reg_kwargs["selection"] = check_param_for_decay

			else:
				reg_cls = WeightDecay

			logging.info(f"Adding {reg_cls.__name__} ({opts.decay:e})")
			self.opt.add_hook(reg_cls(opts.decay, **reg_kwargs))

		if opts.only_head:
			assert not opts.recurrent, "FIX ME! Not supported yet!"

			logging.warning("========= Fine-tuning only classifier layer! =========")
			self.model.disable_update()
			self.model.fc.enable_update()

	def init_model(self, opts):
		"""creates backbone CNN model. This model is wrapped around the classifier later"""

		self.model = ModelType.new(
			model_type=self.model_info.class_key,
			input_size=opts.input_size,
			**self.model_kwargs,
			# pooling=opts.pooling,
			# pooling_params=dict(
			# 	init_alpha=opts.init_alpha,
			# 	output_dim=8192,
			# 	normalize=opts.normalize),
			# aux_logits=False
		)

	def load_model_weights(self, args):
		if args.from_scratch:
			logging.info("Training a {0.__class__.__name__} model from scratch!".format(self.model))
			loader = self.model.reinitialize_clf
			self.weights = None
		else:
			if args.load:
				self.weights = args.load
				logging.info("Loading already fine-tuned weights from \"{}\"".format(self.weights))
				loader = partial(self.model.load_for_inference, weights=self.weights)
			else:
				self.weights = join(
					self.data_info.BASE_DIR,
					self.data_info.MODEL_DIR,
					self.model_info.folder,
					self.model_info.weights
				)
				logging.info("Loading pre-trained weights \"{}\"".format(self.weights))
				loader = partial(self.model.load_for_finetune, weights=self.weights)

		if hasattr(self.clf, "output_size"):
			feat_size = self.clf.output_size

		if hasattr(self.clf, "loader"):
			loader = self.clf.loader(loader)

		logging.info(f"Part features size after encoding: {feat_size}")
		loader(n_classes=self.n_classes, feat_size=feat_size)
		self.clf.cleargrads()

class _DatasetMixin(abc.ABC):
	"""
		This mixin is responsible for annotation loading and for
		dataset and iterator creation.
	"""

	def __init__(self, dataset_cls, *args, **kwargs):
		super(_DatasetMixin, self).__init__(*args, **kwargs)
		self.dataset_cls = dataset_cls

	@property
	def n_classes(self):
		return self.part_info.n_classes + self.dataset_cls.label_shift

	def new_dataset(self, opts, size, subset, augment):
		"""Creates a dataset for a specific subset and certain options"""
		kwargs = dict(
			subset=subset,
			dataset_cls=self.dataset_cls,
		)

		# if opts.use_parts:
		# 	kwargs.update(dict(
		# 		no_glob=opts.no_global,
		# 	))

		if not opts.only_head:
			kwargs.update(dict(
				preprocess=self.prepare,
				augment=augment,
				size=size,
				center_crop_on_val=not opts.no_center_crop_on_val,

			))

		d = self.annot.new_dataset(**kwargs)
		logging.info("Loaded {} images".format(len(d)))
		logging.info("Data augmentation is {}abled".format("en" if augment else "dis"))
		# logging.info("Global feature is {}used".format("not " if opts.no_global else ""))
		return d

	def init_annotations(self, opts):
		"""Reads annotations and creates annotation instance, which holds important infos about the dataset"""

		annot_cls = AnnotationType.get(opts.dataset).value
		self.annot = annot_cls(opts.data, opts.parts)

		self.data_info = self.annot.info
		self.model_info = self.data_info.MODELS[opts.model_type]
		self.part_info = self.data_info.PARTS[opts.parts]

		if opts.only_head:
			self.annot.feature_model = opts.model_type

	def init_datasets(self, opts):

		self.dataset_cls.label_shift = opts.label_shift

		size = self.model.meta.input_size

		self.prepare = partial(PrepareType[opts.prepare_type](self.model),
			swap_channels=opts.swap_channels,
			keep_ratio=not opts.no_center_crop_on_val,
		)

		logging.info(" ".join([
			f"Created {self.model.__class__.__name__} model",
			f"with \"{opts.prepare_type}\" prepare function.",
			f"Image input size: {size}",
		]))

		self.train_data = self.new_dataset(opts, size, "train", True)
		self.val_data = self.new_dataset(opts, size, "test", False)

	def init_iterators(self, opts):
		"""Creates training and validation iterators from training and validation datasets"""

		self.train_iter, _ = new_iterator(self.train_data,
			opts.n_jobs, opts.batch_size
		)

		self.val_iter, _ = new_iterator(self.val_data,
			opts.n_jobs, opts.batch_size,
			repeat=False, shuffle=False
		)

class _TrainerMixin(abc.ABC):
	"""This mixin is responsible for updater, evaluator and trainer creation.
	Furthermore, it implements the run method
	"""

	def __init__(self, updater_cls, updater_kwargs={}, *args, **kwargs):
		super(_TrainerMixin, self).__init__(*args, **kwargs)
		self.updater_cls = updater_cls
		self.updater_kwargs = updater_kwargs

	def init_updater(self):
		"""Creates an updater from training iterator and the optimizer."""
		self.updater = self.updater_cls(
			iterator=self.train_iter,
			optimizer=self.opt,
			device=self.device,
			**self.updater_kwargs,
		)
		logging.info(" ".join([
			f"Using single GPU: {self.device}.",
			f"{self.updater_cls.__name__} is initialized",
			f"with following kwargs: {_format_kwargs(self.updater_kwargs)}"
			])
		)

	def init_evaluator(self, default_name="val"):
		"""Creates evaluation extension from validation iterator and the classifier."""

		self.evaluator = extensions.Evaluator(
			iterator=self.val_iter,
			target=self.clf,
			device=self.device)

		self.evaluator.default_name = default_name

	def run(self, trainer_cls, opts, *args, **kwargs):

		trainer = trainer_cls(
			opts=opts,
			updater=self.updater,
			evaluator=self.evaluator,
			weights=self.weights,
			*args, **kwargs
		)
		def dump(suffix):
			if opts.only_eval or opts.no_snapshot:
				return

			save_npz(join(trainer.out,
				"clf_{}.npz".format(suffix)), self.clf)
			save_npz(join(trainer.out,
				"model_{}.npz".format(suffix)), self.model)

		try:
			trainer.run(init_eval=opts.init_eval or opts.only_eval)
		except (KeyboardInterrupt, BdbQuit) as e:
			raise e
		except Exception as e:
			dump("exception")
			raise e
		else:
			dump("final")


class DefaultFinetuner(_ModelMixin, _DatasetMixin, _TrainerMixin):
	""" The default Finetuner gathers together the creations of all needed
	components and call them in the correct order

	"""

	def __init__(self, opts, *args, **kwargs):
		super(DefaultFinetuner, self).__init__(*args, **kwargs)

		self.gpu_config(opts, *args, **kwargs)

		self.init_annotations(opts)
		self.init_model(opts)

		self.init_datasets(opts)
		self.init_iterators(opts)

		self.wrap_model(opts)
		self.load_model_weights(opts)

		self.init_optimizer(opts)
		self.init_updater()
		self.init_evaluator()

	def gpu_config(self, opts, *args, **kwargs):
		if -1 in opts.gpu:
			self.device = -1
		else:
			self.device = opts.gpu[0]
		cuda.get_device_from_id(self.device).use()

