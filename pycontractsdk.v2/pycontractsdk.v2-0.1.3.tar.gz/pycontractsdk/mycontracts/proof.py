#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-07-31 14:44:41
LastEditors:  
LastEditTime: 2019-07-31 14:44:41
Description:  
"""

from pycontractsdk.contracts import Contract


class Proof(Contract):
    def __init__(self, provider, timeout=60, *args, **kwargs):
        super(Proof, self).__init__(provider, timeout, *args, **kwargs)

    def submitProof(self, address, level, proofHash, metaData):
        """ submitProof """
        contract = self.get_contract()
        submitProof_function = contract.functions.submitProof(address, level, proofHash, metaData)
        tf, tx_hash = self.upload_function(submitProof_function, self._private_key)
        timeout = self.waitForTx(tx_hash)
        return tf, tx_hash
