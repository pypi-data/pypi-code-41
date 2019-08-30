#
# COPYRIGHT
#
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#

from keras.callbacks import ModelCheckpoint


class ExtendedModelCheckpoint(ModelCheckpoint):
    def set_anchors(self, anchors):
        self.anchors = anchors

    def on_epoch_end(self, epoch, logs=None):
        update = False
        current = logs.get(self.monitor)
        if current is not None:
            if self.monitor_op(current, self.best):
                update = True
        super(ExtendedModelCheckpoint, self).on_epoch_end(epoch, logs)

        if update:
            #############################################
            # Save meta data about the model
            #############################################
            import h5py
            with h5py.File(self.filepath, mode='r+') as f:
                f["anchors"] = self.anchors

