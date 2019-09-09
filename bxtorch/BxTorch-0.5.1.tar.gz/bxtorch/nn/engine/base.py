#
#  bese.py
#  bxtorch
#
#  Created by Oliver Borchert on 09/05/19.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import os
import time
from abc import ABC, abstractmethod
import torch
import torch.nn as nn
import torch.optim as optim
import torch.cuda as cuda
from torch.utils.data import DataLoader, Dataset, IterableDataset
import bxtorch.multiprocessing as xmp
from bxtorch.nn.callbacks import TrainingCallback, PredictionCallback, \
    CallbackException
import bxtorch.nn.utils as xnnu
from bxtorch.utils.torch import gpu_device, to_device
from bxtorch.utils.stdlib import flatten
from .wrappers import History, Evaluation

class BaseEngine(TrainingCallback, PredictionCallback, ABC):
    """
    A base class for training and evaluating models as well as making 
    predictions. Generally, this class should be seen as _binding_ between a 
    model and some data. Models should always be wrapped in an engine, both 
    when being trained, and when performing inference/evaluation. The 
    engine ensures that the model's environment is correct and prevents plenty 
    of pitfalls.
    
    A concrete implementation of this class is tailored to a specific type of 
    data (e.g. independent, identically distributed data samples) and/or model
    types (e.g. GANs).
    """

    # MARK: Initialization
    def __init__(self, model, dataset_class=None, **dataset_kwargs):
        """
        Initializes a new engine for a specified model.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model to train or evaluate.
        - dataset_class: type like torch.utils.data.Dataset, default: None
            The dataset class to use to make predictions. It must accept as
            first parameter a list of raw elements for prediction. In case no
            class is defined, the ``predict`` function expects to receive a
            dataset or data loader instead of raw elements.
        - dataset_kwargs: keyword arguments
            Arguments passed to the dataset upon initialization.
        """
        self.model = model
        self.device = None
        self._cache = {}
        self._iteration = None

    # MARK: Primary Instance Methods
    def train(self, train_data, val_data=None, epochs=20, val_iterations=None,
              eval_every=None, eval_train=False, callbacks=[], metrics={},
              gpu='auto', **kwargs):
        """
        Method for training the model with the supplied parameters.

        Parameters:
        -----------
        - train_data: torch.DataLoader
            A data loader to obtain training data from. The samples yielded by
            the data loader depend on a specific trainer implementation.
        - val_data: torch.DataLoader, default: None
            A data loader to use for validation. If the loader is an infinite
            data loader, ``val_iterations`` must also be given. If not supplied,
            no validation will be performed.
        - epochs: int, default: 20
            The number of epochs to train for. If the given data is an infinite
            data loader, this value defines the number of iterations (and 
            should most probably be increased).
        - val_iterations: int, default: None
            The number of iterations to perform for validation. Must be given
            only if `val_data` is an infinite data loader. Otherwise, the
            parameter is ignored.
        - eval_every: int, default: None
            How many iterations should pass until validation is called again.
            This should only be set if `train_data` is based on an iterable 
            dataset which has infinite length. Note that everything works as if
            `epochs // eval_every` epochs is trained while eval_every can
            be considered the number of mini-batches.
        - eval_train: bool, default: False
            Whether to compute metrics (apart from the loss) for both the
            validation and the train data. If this flag is set to False,
            metrics will only be computed for the validation data.
        - callbacks: list of bxtorch.nn.TrainingCallback or 
                bxtorch.nn.PredictionCallback, default: []
            The callbacks to use for training and inference. The training
            callbacks and prediction callbacks will be filtered automatically.
        - metrics: dict of str -> func, default: {}
            Metrics to compute during evaluation for the validation data (and
            potentially for the training data). The keys for the metrics define
            their name.
        - gpu: str or bool or int or list of int, default: 'auto'
            Governs, whether training and evaluation should be performed on a
            GPU. If set to True, the GPU with the most amount of free memory is
            selected (if there are multiple GPUs). If set to an integer, the GPU
            with the specified index is used. If set to a list of integers, the
            specified GPUs are used to train and evaluate the model und multiple
            GPUs simultaneously. In this case, the batch sizes of the data
            loaders should be adjusted accordingly. If set to a string, the
            only valid value is 'auto'. In this case, all available GPUs are
            used.
        - kwargs: keyword arguments
            Additional keyword arguments dependent on the specific subclass.

        Returns:
        --------
        - bxtorch.nn.History
            A history object summarizing stats from the training. It contains
            as properties the development of the loss as ``train_loss`` (and
            potentially ``val_loss``, if ``val_data`` is supplied and the 
            keyword arguments include a function called ``loss``). If
            additional metrics are supplied, there will be a property 
            ``val_<metric>`` for each metric, and potentially ``train_<metric>``
            if ``eval_train`` is set to True.
        """
        # 1) Setup
        exception = None
        tic = time.time()

        if eval_every is not None:
            # Here, epochs are considered iterations
            epochs = epochs // eval_every

        # 1.1) Callbacks
        train_callbacks = [
            c for c in callbacks if isinstance(c, TrainingCallback)
        ]
        prediction_callbacks = [
            c for c in callbacks if isinstance(c, PredictionCallback)
        ]

        self._exec_callbacks(
            train_callbacks, 'before_training', self.model, epochs
        )

        # 1.2) Metrics
        metric_history = []
        if 'loss' in kwargs:
            val_metrics = {**metrics, **{'loss': kwargs['loss']}}
        else:
            val_metrics = metrics

        # 1.3) Data loading
        if eval_every is not None:
            train_iterator = iter(train_data)

        # 1.4) GPU support
        if gpu == 'auto':
            if cuda.device_count() == 0:
                gpu = False
            else:
                gpu = list(range(cuda.device_count))
        self._setup_device(gpu)
        self.model.to(self.device)
        
        # 2) Train for number of epochs
        for current_epoch in range(epochs):
            # 2.1) Prepare
            batch_iterations = eval_every or len(train_data)
                
            try:
                self._exec_callbacks(
                    train_callbacks, 'before_epoch', current_epoch, 
                    batch_iterations
                )
            except CallbackException as e:
                exception = e
                break

            # 2.2) Train
            self.model.train()

            train_batch_weights = []
            train_losses = []

            if eval_every is not None:
                # 2.2.1) Iterable dataset
                for _ in range(eval_every):
                    item = next(train_iterator)
                    item = to_device(self.device, item)
                    loss = self.train_batch(item, **kwargs)
                    train_losses.append(loss)
                    self._exec_callbacks(
                        train_callbacks, 'after_batch'
                    )
            else:
                # 2.2.2) Dataset
                for item in train_data:
                    item = to_device(self.device, item)
                    loss = self.train_batch(item, **kwargs)
                    train_batch_weights.append(len(item))
                    train_losses.append(loss)
                    self._exec_callbacks(
                        train_callbacks, 'after_batch'
                    )

            # 2.3) Validate
            batch_metrics = Evaluation(
                self.collate_train_losses(train_losses),
                train_batch_weights
            )

            if val_data is not None:
                eval_val = self.evaluate(
                    val_data, iterations=val_iterations, metrics=val_metrics,
                    callbacks=prediction_callbacks, gpu=None
                ).with_prefix('val_')
                batch_metrics = Evaluation.merge(batch_metrics, eval_val)

            if eval_train:
                eval_train = self.evaluate(
                    train_data, iterations=val_iterations, metrics=metrics,
                    callbacks=prediction_callbacks, gpu=None
                ).with_prefix('train_')
                batch_metrics = Evaluation.merge(batch_metrics, eval_train)

            batch_metrics = Evaluation.merge(
                batch_metrics, Evaluation({'_timestamp': time.time()})
            )

            metric_history.append({
                'micro_train_loss': train_losses,
                **batch_metrics.to_dict()
            })

            # 2.4) Finish epoch
            try:
                self._exec_callbacks(
                    train_callbacks, 'after_epoch', batch_metrics
                )
            except CallbackException as e:
                exception = e
                break

        # 3) Finish training
        # 3.1) If GPU used
        if gpu is not None:
            self.model.to('cpu', non_blocking=True)
            self.device = None

        # 3.2) Finish callbacks
        self._exec_callbacks(
            train_callbacks, 'after_training'
        )
        if exception is not None:
            print(exception)

        return History(time.time() - tic, metric_history)

    def evaluate(self, data, iterations=None, metrics={}, callbacks=[],
                 gpu='auto'):
        """
        Evaluates the model on the given data and computes the supplied metrics.

        Parameters:
        -----------
        - data: torch.DataLoader
            A data loader to obtain evaluation samples from. The expected 
            samples depend on a specific trainer subclass.
        - iterations: int, default: None
            The number of samples used for evaluating if the given data is an
            infinite data loader.
        - metrics: dict of str -> func, default: {}
            The metrics to evaluate the model for. The keys define the names of
            the metrics when retrieving the evaluated result from the return
            parameter.
        - callbacks: list of bxtorch.nn.PredictionCallback, default: []
            Callbacks to use while computing predictions. Usually, they are 
            used for logging.
        - gpu: str or bool or int or list of int, default: False
            Governs, whether training and evaluation should be performed on a
            GPU. If set to True, the GPU with the most amount of free memory is
            selected (if there are multiple GPUs). If set to an integer, the GPU
            with the specified index is used. If set to a list of integers, the
            specified GPUs are used to train and evaluate the model und multiple
            GPUs simultaneously. In this case, the batch sizes of the data
            loaders should be adjusted accordingly. If set to 'auto', all
            available GPUs are used. In case of `None`, the model will not be
            moved. Only use this option if you know what you are doing.

        Returns:
        --------
        - bxtorch.nn.training.wrappers.Evaluation
            An evaluation object, yielding as properties the metrics with their
            specified names.
        """
        num_predictions = iterations or len(data)
        self._exec_callbacks(
            callbacks, 'before_predictions', self.model, num_predictions
        )

        if gpu is not None:
            if gpu == 'auto':
                if cuda.device_count() > 0:
                    gpu = list(range(cuda.device_count()))
                else:
                    gpu = False
                    
            self._setup_device(gpu)
            self.model.to(self.device)

        self.model.eval()

        predictions = []
        targets = []

        iterator = iter(data)
        for _ in range(num_predictions):
            item = next(iterator)
            item = to_device(self.device, item)

            with torch.no_grad():
                prediction, target = self.eval_batch(item)

            predictions.append(to_device('cpu', prediction))
            targets.append(to_device('cpu', target))

            self._exec_callbacks(
                callbacks, 'after_batch'
            )

        self._exec_callbacks(
            callbacks, 'after_predictions'
        )
        
        predictions = self.collate_predictions(predictions)
        targets = self.collate_targets(targets)

        def process_metric(k, m):
            if isinstance(m, dict):
                return [(f'{k}_{mk}', mm.item()) for mk, mm in m.items()]
            return [(k, m.item())]
        
        result = dict(flatten(
            process_metric(k, f(predictions, targets))
            for k, f in metrics.items()
        ))

        if gpu is not None:
            self.model.to('cpu', non_blocking=True)
            self.device = None

        return Evaluation(result)

    def predict(self, data, iterations=None, callbacks=[], gpu='auto',
                **kwargs):
        """
        Computes predictions for the given samples.

        Parameters:
        -----------
        - data: torch.Dataset or torch.DataLoader
            If a data loader is given, it is used directly, otherwise the
            dataset is wrapped into a data loader. Generally, you should prefer
            passing a dataset since the predict function will then make sure
            that items are sampled sequentially from the dataset, and batches
            are pinned when using a GPU.
        - iterations: int, default: None
            The (maximum) number of samples used for evaluating if the given 
            data is an iterable dataset.
        - callbacks: list of bxtorch.nn.PredictionCallback
            Callbacks which are called as prediction progresses.
        - gpu: str or bool or int or list of int, default: 'auto'
            Whether to use a (specific) GPU or multiple GPUs. If multiple GPUs
            are used, one process per GPU is started to minimize
            synchronization overhead. Make sure that using multiple GPUs makes 
            up for this overhead. If ``False`` is specified, all cores of the 
            computer are used to make predictions in parallel. In the case of
            'auto', all available GPUs are used (if any).
        - kwargs: keyword arguments
            Additional arguments fed directly to the data loader. Includes e.g.
            ``batch_size``.

        Returns:
        --------
        - torch.Tensor
            The predictions made by the model.
        - torch.Tensor or object
            The collated targets if `for_eval` is specified.
        """
        # 1) Set gpu if all is specified
        if gpu == 'auto':
            if cuda.device_count() > 0:
                gpu = list(range(cuda.device_count()))
            else:
                gpu = False

        # 2) Get data loader
        if isinstance(data, DataLoader):
            loader = data
        else:
            assert isinstance(data, Dataset), \
                "Data must be either a data loader or a dataset."

            # kwargs['pin_memory'] = isinstance()
            kwargs['shuffle'] = False
            loader = data.loader(**kwargs)
        
        num_iterations = iterations or len(loader)

        self._exec_callbacks(
            callbacks, 'before_predictions', self.model, num_iterations
        )

        # 3) Make sure that the model is not data parallel, we don't need this
        #    for predicting
        if isinstance(self.model, nn.DataParallel):
            model = self.model.module.eval()
        else:
            model = self.model.eval()

        # 4) Now perform predictions
        if (isinstance(gpu, list) and len(gpu) > 1) or gpu == False: 
            # parallel computation
            if isinstance(gpu, list):
                num_workers = len(gpu)
            elif isinstance(gpu, bool):
                num_workers = os.cpu_count()
            else:
                num_workers = 1

            model.share_memory()

            callback = lambda:self._exec_callbacks(callbacks, 'after_batch')
            vectorizer = xmp.Vectorizer(
                _prediction_worker_func, _prediction_worker_init, 
                callback_func=callback, num_workers=num_workers,
                gpu=gpu, model=model
            )

            predictions = vectorizer.process(
                loader, model, self.process_prediction
            )
        else: 
            # sequential computation
            device = gpu_device(gpu[0] if isinstance(gpu, list) else gpu)
            model = model.to(device)

            predictions = []

            for x in loader:
                out = _prediction_worker_func(
                    x, model, self.process_prediction, device
                )
                predictions.append(out)
                self._exec_callbacks(
                    callbacks, 'after_batch'
                )

        self._exec_callbacks(
            callbacks, 'after_predictions'
        )

        return self.collate_predictions(predictions)

    # MARK: Secondary Instance Methods
    def optimizer(self, optimizer='adam', **kwargs):
        """
        Convenience function to create an optimizer for the model from a string.

        Parameters:
        -----------
        - optimizer: str, default: 'adam'
            The optimizer to use. Acceptable values are all optimizers from
            torch.optim (upper and lowercase does not matter).
        - kwargs: keyword arguments
            Arguments passed to the optimizer during initalization.
        """
        valid_optimizers = [
            'ASGD', 'Adadelta', 'Adagrad', 'Adam', 'Adamax', 'LBFGS',
            'RMSprop', 'Rprop', 'SGD', 'SparseAdam'
        ]
        for opt in valid_optimizers:
            if opt.lower() == optimizer.lower():
                return getattr(optim, opt)(self.model.parameters(), **kwargs)
        raise ValueError(f'Invalid optimizer {optimizer}.')

    # MARK: Overrideable Instance Methods
    @abstractmethod
    def train_batch(self, data, **kwargs):
        """
        Runs a single step in training. If the training data represents an 
        infinite dataset, this equals a single iteration, otherwise a 
        mini-batch.

        Parameters:
        -----------
        - data: object
            The data for the current iteration/mini-batch.

        Returns:
        --------
        - object
            The loss computed for the batch. If the returned value is not float,
            overwrite collate_train_losses`.
        """
        pass

    @abstractmethod
    def eval_batch(self, data, **kwargs):
        """
        Runs a single step for inference. The data is either a mini-batch or a 
        single iteration, depending on the data used for evaluation.

        Parameters:
        -----------
        - data: object
            The data for the current iteration/mini-batch.
        - kwargs: keyword arguments
            Additional arguments dependent on the subclass and passed directly
            from the evaluation method.

        Returns:
        --------
        - torch.Tensor
            The output from the model.
        - object
            The target, i.e. correct output. If this is not a ``torch.Tensor``, 
            the ``collate_targets`` should be overriden.
        """
        pass

    def process_prediction(self, x, out):
        """
        Processes a single batch of predictions based on the input and output.
        The default implementation simply returns the output but in some cases
        it might be desirable to have knowledge of the input to enrich the
        output with some information. The output of this function will be
        passed to the `collate_predictions` function.

        Parameters:
        -----------
        - x: torch.Tensor
            The batch inputted to the model.
        - out: torch.Tensor
            The output of the model.

        Returns:
        --------
        - object
            The return value passed to `collate_predictions`.
        """
        return out

    def collate_predictions(self, predictions):
        """
        Combines the predictions obtained from the `eval_batch` function.
        The default implementation assumes that predictions are tensors and can 
        simply be conatenated.

        Parameters:
        -----------
        - predictions: list of objects
            The predictions.

        Returns:
        --------
        - object
            An object to be used as predicted value for some metric.
        """
        return torch.cat(predictions)

    def collate_targets(self, targets):
        """
        Combines the targets in a way that it can be passed to some metric.
        The default implementation assumes that targets are tensors and simply
        concatenates them.

        Parameters:
        -----------
        - list of object
            The targets.

        Returns:
        --------
        - object
            An object to be used as true target with some metric.
        """
        return torch.cat(targets)

    def collate_train_losses(self, losses):
        """
        Combines the losses obtained from the `train_batch function.
        The default implementation assumes that simple floats are returned.

        Parameters:
        -----------
        - losses: list of object
            The losses returned from `train_batch`.
        
        Returns:
        --------
        - dict of str -> (float or list of float)
            The loss names mapped to their values.
        """
        return {'train_loss': losses}

    # MARK: Private Methods
    def _setup_device(self, gpu):
        if isinstance(gpu, list) and len(gpu) > 1:
            self.model = xnnu.DataParallel(self.model, device_ids=gpu)
            self.device = gpu_device(gpu[0])
        else:
            self.device = gpu_device(gpu[0] if isinstance(gpu, list) else gpu)

    def _exec_callbacks(self, callbacks, func, *args):
        for callback in ([self] + callbacks):
            getattr(callback, func)(*args)

    def _forward(self, x):
        return _forward(self.model, x)


def _prediction_worker_func(item, model, process, device):
    x = to_device(device, item)
    with torch.no_grad():
        out = _forward(model, x)
    return to_device('cpu', process(x, out))


def _prediction_worker_init(rank, gpu, model):
    if isinstance(gpu, list):
        device = gpu_device(gpu[rank])
    else:
        device = gpu_device(gpu)
    model.to(device)
    return device


def _forward(model, x):
    if isinstance(x, (list, tuple)):
        return model(*x)
    elif isinstance(x, dict):
        return model(**x)
    else:
        return model(x)
