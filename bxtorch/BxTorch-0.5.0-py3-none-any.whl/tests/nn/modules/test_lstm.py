#
#  nn/modules/test_lstm.py
#  bxtorch/tests
#
#  Created by Oliver Borchert on June 13, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import unittest
import time
import numpy as np
import torch
import torch.nn as nn
from bxtorch.nn.modules.lstm import _LSTMCell

class TestLSTM(unittest.TestCase):

    def test_lstm_cell(self):
        nn_lstm = nn.LSTMCell(2, 2, bias=False)
        xnn_lstm = _LSTMCell(2, 2, bias=False)

        for _ in range(50):
            x = torch.rand(2).view(1, -1)
            hidden = torch.rand(2).view(1, -1)
            state = torch.rand(2).view(1, -1)

            val = float(np.random.rand(1))
            for p in nn_lstm.parameters():
                nn.init.constant_(p, val)
            for p in xnn_lstm.parameters():
                nn.init.constant_(p, val)

            with torch.no_grad():
                out_true = nn_lstm(x, (hidden, state))
                out_ours = xnn_lstm(x, (hidden, state))

            self.assertTrue(
                (out_true[0].numpy() == out_ours[0].numpy()).all()
            )
            self.assertTrue(
                (out_true[1].numpy() == out_ours[1].numpy()).all()
            )
        

if __name__ == '__main__':
    unittest.main()