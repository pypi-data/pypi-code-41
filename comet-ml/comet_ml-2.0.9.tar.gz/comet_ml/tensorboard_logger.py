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
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************


import logging

from comet_ml._logging import check_module
from comet_ml.utils import Histogram

LOGGER = logging.getLogger(__name__)
LOG_METRICS = True
LOG_HISTOGRAMS = False


def extract_from_add_summary(file_writer, summary, global_step):
    from tensorflow.core.framework import summary_pb2

    extracted_values = {"params": {}, "histo": []}

    if isinstance(summary, bytes):
        summ = summary_pb2.Summary()
        summ.ParseFromString(summary)
        summary = summ

    for value in summary.value:
        field = value.WhichOneof("value")

        if field == "simple_value":
            extracted_values["params"][value.tag] = value.simple_value
        elif field == "histo":
            extracted_values["histo"].append(value.histo)

    return extracted_values, global_step


def convert_histograms(histo):
    """
    Convert tensorboard summary histogram format into a Comet histogram.
    """
    histogram = Histogram()
    values = histo.bucket_limit
    counts = histo.bucket
    histogram.add(values, counts)
    return histogram


def add_summary_logger(experiment, original, value, *args, **kwargs):
    try:
        if LOG_METRICS or LOG_HISTOGRAMS:

            LOGGER.debug("TENSORBOARD LOGGER CALLED")
            values, step = extract_from_add_summary(*args, **kwargs)
            if values["params"] and LOG_METRICS:
                experiment.log_metrics(values["params"], step=step)
            if values["histo"] and LOG_HISTOGRAMS:
                for histo in values["histo"]:
                    experiment.log_histogram_3d(convert_histograms(histo), step=step)

    except Exception:
        LOGGER.error(
            "Failed to extract parameters/histograms from add_summary()", exc_info=True
        )


class ContextHolder:
    def __init__(self, new_context):
        self.new_context = new_context
        self.old_context = None

    def enter(self, experiment, *args, **kwargs):
        self.old_context = experiment.context
        experiment.context = self.new_context

    def exit(self, experiment, *args, **kwargs):
        experiment.context = self.old_context
        self.old_context = None


TRAIN_HOLDER = ContextHolder("train")
EVAL_HOLDER = ContextHolder("eval")


def patch(module_finder):
    check_module("tensorflow")
    check_module("tensorboard")

    # Register the fit methods
    module_finder.register_after(
        "tensorflow.summary", "FileWriter.add_summary", add_summary_logger
    )
    module_finder.register_before(
        "tensorflow.python.estimator.estimator", "Estimator.train", TRAIN_HOLDER.enter
    )
    module_finder.register_after(
        "tensorflow.python.estimator.estimator", "Estimator.train", TRAIN_HOLDER.exit
    )
    module_finder.register_before(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.train",
        TRAIN_HOLDER.enter,
    )
    module_finder.register_after(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.train",
        TRAIN_HOLDER.exit,
    )
    module_finder.register_before(
        "tensorflow.python.estimator.estimator", "Estimator.evaluate", EVAL_HOLDER.enter
    )
    module_finder.register_after(
        "tensorflow.python.estimator.estimator", "Estimator.evaluate", EVAL_HOLDER.exit
    )
    module_finder.register_before(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.evaluate",
        EVAL_HOLDER.enter,
    )
    module_finder.register_after(
        "tensorflow_estimator.python.estimator.estimator",
        "Estimator.evaluate",
        EVAL_HOLDER.exit,
    )


check_module("tensorflow")
check_module("tensorboard")
