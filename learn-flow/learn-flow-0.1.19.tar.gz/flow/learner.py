# -*- coding: utf-8 -*-
"""
module learner.py
--------------------
A base class definition for the learner class.
The default learner defines steps for the learning procedure.
"""
import tensorflow as tf
import numpy as np
from .callbacks import before_session_initialization, on_batch_begin, on_batch_end, on_train_begin, on_epoch_begin
from .callbacks import validate_sig, on_validate_begin, on_validate_end, on_epoch_end, on_train_end


class ModelValidator(object):
    """
    Default Model Validation runner.
    """
    def __init__(self, model):
        """ Validator initializer."""
        self.model = model
        # connect to the on_epoch_end callback
        validate_sig.connect(self.validate_model, weak=False)

    def validate_model(self, sender):
        """Model validation."""

        if self.model._valid_dataset is not None:
            # re-triggers the on_validate_begin event
            on_validate_begin.send(sender)
            # ensures that learning_pahse is False
            self.model.is_training_phase = False
            results = self.evaluate()
            for key, value in results.items():
                if key.startswith("valid_"):
                    sender.current_state[key] = value
                else:
                    sender.current_state["valid_" + key] = value
        # re-trigger the on_validate_end event
        on_validate_end.send(sender)

    def evaluate(self):
        """Evaluate."""
        results = self.model.evaluate(self.model._valid_dataset)
        return results


class DefaultLearner(object):
    """
    Defines the default learning steps and procedures for fitting models.
    """
    def __init__(self, model, outputs, optimizer, loss_name="loss", resume=False):
        """
        Default learner initializer.
        :param model: reference to the model object
        :param outputs: a dictionary of outputs.
        :param optimizer: the optimizer to be used.
        :param loss_name: loss tensor name.
        """
        self.model = model
        self.config = self.model.config
        self.outputs = outputs
        self.optimizer = optimizer
        # self._update_opt = update_opt
        self.global_step = tf.train.get_or_create_global_step()
        self._update_opt = optimizer.minimize(outputs[loss_name], global_step=self.global_step)
        self.validator = ModelValidator(self.model)
        self.current_state = dict()

        # flag used to signaling when it should stop learning loop.
        self._stop_flag = False
        before_session_initialization.send(self.model)
        self._initialize_session()
        if resume:
            p = self.config.get("flow.premodel")
            self.model.load(tf.train.latest_checkpoint(p))

    @staticmethod
    def _get_accumulators(outputs: dict):
        """
        builds and returns a dictionary containing a key for each step output.
        The outputs of each learning step is stored on this dictionary.
        :param outputs: A dictionary containing the learning step outputs.
        """
        accumulators = dict()
        for output_name in outputs.keys():
            accumulators[output_name] = list()
        return accumulators

    def _aggregate_accumulators(self, accumulators: dict):
        """
        Averages all learning step outputs for one epoch.
        :param accumulators: epoch outputs values.
        """
        # on epoch end triggers
        for output_name, output_vals in accumulators.items():
            self.current_state[output_name] = np.mean(output_vals)

    def epoch_fit_loop(self, outputs):
        """
        Fit inner loop for one learning epoch.
        :param outputs: a dictionary of outputs.
        """
        accumulators = self._get_accumulators(outputs)
        try:
            # ensures training phase is True
            self.model.is_training_phase = True
            while True:
                # on batch begin triggers
                on_batch_begin.send(self)
                # run session and and perform learning step.
                batch_outs = self.learn_step(outputs)
                # # accumulate outputs
                for out_name, outvals in batch_outs.items():
                    accumulators[out_name].append(outvals)
                # on batch end triggers
                on_batch_end.send(self)
        except tf.errors.OutOfRangeError:
            pass
        return accumulators

    def learn_step(self, outputs):
        """defines one leaning iteration step."""
        try:
            outputs["update_opt"] = self._update_opt
            sess = tf.get_default_session()
            ret = sess.run(
                fetches=outputs
            )
            ret.pop("update_opt")
            return ret
        finally:
            outputs.pop("update_opt")

    def fit(self):
        """
        Learning fit function. Starts the fitting procedure.
        :return:
        """
        self._stop_flag = False
        # on train begin triggers
        on_train_begin.send(self)
        # main loop
        for epoch_i in range(int(self.model.config["FLOW.N_EPOCHS"])):
            self.current_state["current_epoch"] = epoch_i
            # on epoch begin trigger
            on_epoch_begin.send(self)

            # epoch begin trigger
            accumulators = self.epoch_fit_loop(self.outputs)
            self._aggregate_accumulators(accumulators)
            validate_sig.send(self)
            on_epoch_end.send(self)

            # print(">>>>current_state>>>", self.current_state)
            print(
                "Epoch '{i}'=> loss: {loss:0.5f}, ".format(
                    i=self.current_state["current_epoch"] + 1,
                    loss=self.current_state["loss"]
                ), self.current_state
            )

            # checks when the stop train flag is set to true
            # and break the main training loop when it happens
            if self._stop_flag:
                break

        # on train end triggers
        on_train_end.send(self)

    def _initialize_session(self):
        """Default session initialization function."""
        if not self.model._is_session_initialized:
            # tf global variables initialization (session variables initialization)
            # sess = tf.get_default_session()
            # sess.run(tf.global_variables_initializer())
            # self.model._is_session_initialized = True
            sess = tf.get_default_session()
            not_initialized = sess.run([tf.is_variable_initialized(var) for var in tf.global_variables()])
            not_initialized = [v for (v, f) in zip(tf.global_variables(), not_initialized) if not f]
            if len(not_initialized) > 0:
                sess.run(tf.variables_initializer(not_initialized))
            self.model._is_session_initialized = True
