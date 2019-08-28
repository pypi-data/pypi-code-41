# -*- coding: utf-8 -*-
"""
module history.py
--------------------------------
Saves the training metrics history after every epoch.
"""
import numpy as np
import tensorflow as tf
import os
import tarfile
import json
from . import ModeEnum
from ..numpy_encoder import NumpyEncoder
from flow.callbacks import on_batch_begin, on_batch_end, on_epoch_begin, on_epoch_end, on_train_begin, \
    on_train_end, on_validate_begin, on_validate_end


class History(object):
    """Saves the training metrics history after every epoch.
    """

    def __init__(self, path, add_keys=None):
        """
        History callback initialization.
        """
        self._hists = dict()
        self.path = path
        self.add_keys = add_keys
        on_epoch_end.connect(self.on_epoch_end, weak=False)

    def on_epoch_end(self, sender):
        epoch = sender.current_state["current_epoch"]
        model = sender.model
        names = self._get_metric_names(model)
        names.append("loss")
        names.append("valid_loss")
        if self.add_keys is not None:
            for key in self.add_keys:
                names.append(key)

        for n in names:
            if n not in self._hists:
                self._hists[n] = list()
            val = sender.current_state.get(n, None)
            self._hists[n].append(val)
            self._hists["ep"] = epoch
            with open(self.path + "_history.json", mode="w", encoding='utf-8') as f:
                json.dump(self._hists, f, cls=NumpyEncoder)


    def _get_metric_names(self, model):
        names = list()
        for m in model._metrics:
            names.append(m.name.split(":")[0])
        for l in model._losses:
            names.append(l.name.split(":")[0])
        return names
