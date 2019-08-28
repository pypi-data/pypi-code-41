# coding=utf-8
"""
module dataset.py
__________________________________
Base dataset wrapper definition.
"""
import tensorflow as tf
from .config.config import Config
from blinker import signal

on_epoch_begin = signal("on_epoch_begin")
before_session_initialization = signal("before_session_initialization")
on_validate_begin = signal("on_validate_begin")


class Dataset(object):

    def __init__(self, inputs_config, config: Config=None, path=None, iterator=None, partition="train", *args, **kwargs):
        # configurations
        self.path = path
        self.partition = partition
        self._inputs_config = inputs_config
        self.config = config
        # build dataset
        self._dataset = self.build_dataset()

        self._iterator = iterator
        self._iterator_initializer = None
        before_session_initialization.connect(self.get_iterator_initializer, weak=True)
        if self.partition == "train":
            on_epoch_begin.connect(self.initialize_iterator, weak=False)
        elif self.partition == "valid":
            on_validate_begin.connect(self.initialize_iterator, weak=False)
        elif self.partition == "test":
            pass

    def get_iterator_initializer(self, sender):
        """
        Returns the iterator initializer op.
        :param sender: the function caller object.
        """
        if self._iterator_initializer is None:
            if self._iterator is None:
                self._iterator = self.get_iterator()
            self._iterator_initializer = self._iterator.make_initializer(self._dataset)
        return self._iterator_initializer

    def initialize_iterator(self, sender):
        """
        Initializes the current dataset iterator by runing the iterator initializer on the current session.
        :param sender: the function caller object
        """
        if self._iterator_initializer is None:
            self._iterator = self.get_iterator()
            self._iterator_initializer = self.get_iterator_initializer(sender)
        current_session = tf.get_default_session()
        current_session.run(self._iterator_initializer)

    def restart(self):
        """
        Restart iterations from the first sequence element.
        **A hook to 'self.initialize_iterator'.**
        """
        self.initialize_iterator(None)

    def get_iterator(self):
        """
        creates the dataset iteretor tensor to be used in tensorflow.
        :return: the tensorflow dataset iterator.
        """
        # a function to be called when no other custom function is provided.
        if self._dataset is None:
            self._dataset = self.build_dataset()
        self._iterator = self._dataset.make_initializable_iterator()
        return self._iterator

    def build_dataset(self):
        batch_size = int(self.config.get("FLOW.BATCH_SIZE", 1))
        prefetch_buffer = 100
        dataset = tf.data.Dataset.from_generator(
            generator=lambda: iter(self),
            output_types=self._inputs_config["output_types"],
            output_shapes=self._inputs_config["output_shapes"]
        )
        dataset = dataset.batch(batch_size)
        return dataset.prefetch(buffer_size=prefetch_buffer)

    def set_iterator(self, iterator):
        """
        sets dataset iterator.
        :param iterator: tf.dataset.iterator instance.
        """
        self._iterator = iterator
