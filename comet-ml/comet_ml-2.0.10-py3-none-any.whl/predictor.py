# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import logging

from .api import API
from .config import get_config
from .connection import get_backend_session

LOGGER = logging.getLogger(__name__)


class Predictor(object):
    """
    Please email lcp-beta@comet.ml for comments or questions.
    """

    def __init__(
        self,
        experiment,
        loss_name="loss",
        patience=10,
        best_callback=None,
        threshold=0.1,
        api=None,
        optimizer_id=None,
        interval=2,
        start=5,
        mode="local",
        **defaults
    ):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.config = get_config()
        self.experiment = experiment

        self.allowed_modes = ["global", "local"]
        if mode in self.allowed_modes:
            self.mode = mode

        else:
            msg = "{} mode not supported. Please set mode to global or local"
            raise ValueError(msg.format(mode))

        self.loss_name = loss_name
        self.patience = patience
        self.best_callback = best_callback
        self.step = None
        self.done = None
        self.wait = 0
        self.best = None
        self.loss = []
        self.defaults = {
            "experiment_key": self.experiment.id,
            "api_key": self.experiment.api_key,
            "TS": self.loss,  # Reference!
            "HP_samples": float("nan"),
            "AP_no_parameters": float("nan"),
            "HP_epochs": float("nan"),
            "HP_learning_rate": float("nan"),
            "HP_batch_size": float("nan"),
        }
        self.set_defaults(**defaults)
        self.threshold = threshold
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("Threshold must be set between 0.0 and 1.0")

        self.base_url = self.config["comet.predictor_url"]
        self.status_url = "{}lc_predictor/status/".format(self.base_url)
        self.predict_url = "{}lc_predictor/predict/".format(self.base_url)
        self._session = get_backend_session()
        status = self.status()
        self.experiment.log_other("predictor_loss_name", self.loss_name)
        self.experiment.log_other("predictor_id", status["model_id"])

        if self.mode == "global":
            # Check if optimizer_id is set
            if self.experiment.optimizer is None:
                if optimizer_id is None:
                    raise ValueError(
                        "Please set an optimizer id to use the Predictor in global mode"
                    )
                else:
                    self.optimizer_id = optimizer_id
                    self.experiment.log_other("optimizer_id", self.optimizer_id)

            else:
                self.optimizer_id = self.experiment.optimizer["optimizer"].id

            # Specifies the number of experiment to include in the sample period
            self.start = start
            self.interval = interval

            # If interval is set to 0
            if not self.interval >= 1:
                raise ValueError("Please set interval to at least 1")

            self.api = api if api else API()
            self.predictions = []

        else:
            LOGGER.warning("Predictor Local Mode is still experimental.")

    def reset(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.step = None
        self.wait = 0
        self.best = None
        self.loss[:] = []  # Reference!

    def set_defaults(self, **defaults):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.defaults.update(defaults)

    def status(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            response = self._session.get(self.status_url)
        except Exception:
            LOGGER.debug("Error getting the status", exc_info=True)
            pass
        else:
            if response.status_code == 200:
                response_data = response.json()
                return response_data
            else:
                LOGGER.debug("Invalid status code %d", response.status_code)
        return None

    def report_loss(self, loss, step=None):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            loss = float(loss)
        except Exception:
            raise ValueError("Predictor.report_loss() requires a single number")

        self.step = step
        self.loss.append(loss)
        self.experiment.log_metric("predictor_tracked_loss", loss, step=self.step)

    def _local_stop_early(self, **data):
        defaults = self.defaults.copy()
        defaults.update(data)
        if len(self.loss) < 2:
            return False
        if self.done is not None:
            (lower, mean, upper) = self.done
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_upper": upper,
                    "predictor_lower": lower,
                    "predictor_threshold": self.threshold,
                    "predictor_patience": self.patience,
                    "predictor_wait": self.wait,
                },
                step=self.step,
            )
            return True
        lmu = self.get_prediction(**data)
        if lmu is None:
            return False
        (lower, mean, upper) = lmu
        current_loss = self.loss[-1]
        lowest_min = min(self.loss[:-1])
        self.experiment.log_metrics(
            {
                "predictor_mean": mean,
                "predictor_upper": upper,
                "predictor_lower": lower,
                "predictor_threshold": self.threshold,
                "predictor_patience": self.patience,
                "predictor_wait": self.wait,
            },
            step=self.step,
        )
        epoch = self.step if self.step is not None else self.experiment.curr_step
        current_best = min(lowest_min, current_loss)

        # If the loss is improving, reset the wait count
        # Every time we see an improvement, run the callback
        if current_loss < lowest_min:
            self.wait = 0

            self.best = (current_loss, self.experiment.curr_step)
            if callable(self.best_callback):
                self.best_callback(self, current_loss)

        # Else increment the wait count
        else:
            self.wait += 1

        # If tracked loss is less than the predicted loss, stop training
        if current_best <= mean:
            self.experiment.log_other("predictor_stop_step", epoch)
            self.experiment.log_other("predictor_stop_reason", "threshold crossed")
            self.done = (lower, mean, upper)

            return True

        # If patience is exceeded, stop training
        if self.wait >= self.patience:
            self.experiment.log_other("predictor_stop_step", epoch)
            self.experiment.log_other("predictor_stop_reason", "patience exceeded")
            self.done = (lower, mean, upper)

            return True

        return False

    def _global_stop_early(self, epoch, **data):
        defaults = self.defaults.copy()
        defaults.update(data)

        if epoch is None:
            raise ValueError("Please provide epoch value")

        # For cases where model is not stopped after _global_stop_early returns True
        if self.wait >= self.patience:
            LOGGER.debug("Patience Exceeded: %s >= %s", self.wait, self.patience)
            return True

        if self.wait < self.patience:
            lmu = self.get_prediction(**data)
            if lmu is None:
                return False
            (lower, mean, upper) = lmu
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_max": upper,
                    "predictor_min": lower,
                    "predictor_threshold": self.threshold,
                    "predictor_patience": self.patience,
                    "predictor_wait": self.wait,
                }
            )
            self.predictions.append(mean)

            experiment_count, best_metric = self._get_trial_state()
            if (experiment_count is None) or (best_metric is None):
                return False

            # TODO: Move block into its own function
            if experiment_count > self.start:
                if (epoch % self.interval == 0) and (
                    len(self.predictions) >= self.interval
                ):
                    prediction_mean = (
                        sum(self.predictions[-self.interval :]) / self.interval
                    )

                    if prediction_mean > (1 + self.threshold) * best_metric:
                        self.wait += 1

                        if self.wait >= self.patience:
                            self.experiment.log_other("predictor_stop_step", epoch)
                            msg = (
                                "Predicted value {} for metric: {} is higher than the"
                                " best value {} seen in this trial"
                            )
                            self.experiment.log_other(
                                "predictor_stop_reason",
                                msg.format(
                                    prediction_mean,
                                    self.loss_name,
                                    best_metric,
                                    self.threshold,
                                ),
                            )
                            self.done = (lower, prediction_mean, upper)

                            return True

        return False

    def _get_trial_state(self):
        response = self.api.get_optimizer_best(
            self.experiment.id, self.optimizer_id, self.loss_name, maximum=False
        )

        experiment_count = response.get("experimentCount")
        best_metric = response.get("metricValue")

        return experiment_count, best_metric

    def stop_early(self, epoch=None, **data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        if self.mode == "global":
            return self._global_stop_early(epoch, **data)

        else:
            return self._local_stop_early(**data)

    def get_prediction(self, **data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        request_data = self.defaults.copy()
        # Update from one-time overrides:
        request_data.update(data)
        response = self._session.post(
            self.predict_url, json={"data": request_data}, timeout=300
        )
        if response.status_code == 200:
            data = response.json().get("response")
            return data["min"], data["mean"], data["max"]
        elif response.status_code == 201:
            return None
        else:
            raise Exception(
                "Invalid Predictor request for %s: %s" % (request_data, response)
            )
