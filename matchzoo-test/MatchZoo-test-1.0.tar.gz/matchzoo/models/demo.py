"""An implementation of DRMMTKS Model."""
import typing

import torch
import torch.nn as nn
import torch.nn.functional as F

from matchzoo.engine.param_table import ParamTable
from matchzoo.engine.param import Param
from matchzoo.engine.base_model import BaseModel
from matchzoo.engine import hyper_spaces
from matchzoo.modules import Attention
from matchzoo.utils import parse_activation


class Demo(BaseModel):
    """
    DRMMTKS Model.

    Examples:
        >>> model = Demo()
        >>> model.params['top_k'] = 10
        >>> model.params['mlp_num_layers'] = 1
        >>> model.params['mlp_num_units'] = 5
        >>> model.params['mlp_num_fan_out'] = 1
        >>> model.params['mlp_activation_func'] = 'tanh'
        >>> model.guess_and_fill_missing_params(verbose=0)
        >>> model.build()

    """

    @classmethod
    def get_default_params(cls) -> ParamTable:
        """:return: model default parameters."""
        params = super().get_default_params(
            with_embedding=True,
            with_multi_layer_perceptron=True
        )
        params.add(Param(name='mask_value', value=-1,
                         desc="The value to be masked from inputs."))
        params.add(Param(
            'top_k', value=10,
            hyper_space=hyper_spaces.quniform(low=2, high=100),
            desc="Size of top-k pooling layer."
        ))
        params.add(Param(
            name='filters',
            value=128,
            desc="The filter size in the convolution layer."
        ))
        params.add(Param(
            name='conv_activation_func',
            value='relu',
            desc="The activation function in the convolution layer."))
        params.add(Param(
            name='max_ngram',
            value=3,
            desc="The maximum length of n-grams for the convolution "
                 "layer."))
        params.add(Param(
            name='use_crossmatch',
            value=True,
            desc="Whether to match left n-grams and right n-grams of "
                 "different lengths"))
        params['mlp_num_fan_out'] = 1
        return params

    def build(self):
        """Build model structure."""
        self.embedding = self._make_default_embedding_layer()

        self.q_convs = nn.ModuleList()
        self.d_convs = nn.ModuleList()
        for i in range(self._params['max_ngram']):
            conv1 = nn.Sequential(
                nn.ConstantPad1d((0, i), 0),
                nn.Conv1d(
                    in_channels=self._params['embedding_output_dim'],
                    out_channels=self._params['filters'],
                    kernel_size=i + 1,
                ),
                parse_activation(
                    self._params['conv_activation_func']
                )
            )
            self.q_convs.append(conv1)
            self.d_convs.append(conv1)

        self.attention = Attention(
            input_size=self._params['filters'],
            mask=self._params['mask_value']
        )
        self.mlp = self._make_multi_layer_perceptron_layer(
            self._params['top_k']
        )
        self.out = self._make_output_layer(self._params['max_ngram'] ** 2)

    def forward(self, inputs):
        """Forward."""

        # Scalar dimensions referenced here:
        #   B = batch size (number of sequences)
        #   D = embedding size
        #   L = `input_left` sequence length
        #   R = `input_right` sequence length
        #   K = size of top-k

        # Left input and right input.
        # shape = [B, L]
        # shape = [B, R]
        query, doc = inputs['text_left'], inputs['text_right']

        # Process left input.
        # shape = [B, L, D]
        q_embed = self.embedding(query.long()).transpose(1, 2)
        # shape = [B, R, D]
        d_embed = self.embedding(doc.long()).transpose(1, 2)

        q_convs = []
        d_convs = []
        for q_conv, d_conv in zip(self.q_convs, self.d_convs):
            q_convs.append(q_conv(q_embed).transpose(1, 2))
            d_convs.append(d_conv(d_embed).transpose(1, 2))

        KM = []
        for qi in range(self._params['max_ngram']):
            for di in range(self._params['max_ngram']):
                # do not match n-gram with different length if use crossmatch
                if not self._params['use_crossmatch'] and qi != di:
                    continue
                mm = torch.einsum(
                    'bld,brd->blr',
                    F.normalize(q_convs[qi], p=2, dim=-1),
                    F.normalize(d_convs[di], p=2, dim=-1)
                )
                matching_topk = torch.topk(
                    mm,
                    k=self._params['top_k'],
                    dim=-1,
                    sorted=True
                )[0]
                attention_probs = self.attention(q_convs[qi])
                dense_output = self.mlp(matching_topk).squeeze(dim=-1)
                x = torch.einsum('bl,bl->b', dense_output, attention_probs)
                KM.append(x)

        out = self.out(torch.stack(KM, dim=1))
        return out
