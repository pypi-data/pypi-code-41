# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging
import uuid

from ..binding_accessor import BindingAccessor
from ..exceptions import InvalidArgument
from ..rules import RuleCallback

try:
    from sq_native import waf
except ImportError:
    waf = None  # pragma: no cover


LOGGER = logging.getLogger(__name__)


class WAFCB(RuleCallback):
    """ WAF Callback
    """

    def __init__(self, *args, **kwargs):
        super(WAFCB, self).__init__(*args, **kwargs)
        if not self.module_is_available():
            msg = "WAF is disabled because the native module is not installed"
            raise InvalidArgument(msg)

        prefix = uuid.uuid4()
        waf_rule_name = "{}_{}".format(prefix, self.rule_name)

        values = self.data.get("values", {})
        ret = waf.initialize(waf_rule_name, values.get("waf_rules"))
        if ret is not True:
            msg = "failed to initialize the WAF rules"
            raise InvalidArgument(msg)
        self._waf_rule_name = waf_rule_name

        bas = {}
        for expr in values.get("binding_accessors", []):
            bas[expr] = BindingAccessor(expr)
        self.binding_accessors = bas
        self._budget = values.get("budget", 5000)

    def __del__(self):
        waf_rule_name = getattr(self, "_waf_rule_name", None)
        if waf_rule_name is not None:
            waf.clear(waf_rule_name)

    def pre(self, original, *args, **kwargs):
        waf_rule_name = getattr(self, "_waf_rule_name", None)
        request = self.storage.get_current_request()
        if waf_rule_name is None or request is None:
            return

        binding_eval_args = {
            "binding": locals(),
            "global_binding": globals(),
            "framework": request,
            "instance": original,
            "arguments": self.storage.get_current_args(args),
            "kwarguments": kwargs,
            "cbdata": self.data,
            "return_value": None,
        }

        params = {}
        for expr, ba in self.binding_accessors.items():
            params[expr] = ba.resolve(**binding_eval_args)

        LOGGER.debug("WAF run with parameters: %r", params)
        ret = waf.run(waf_rule_name, params, self._budget)
        LOGGER.debug("WAF returned: %r", ret)
        if ret.action in (waf.PW_BLOCK, waf.PW_MONITOR):
            self.record_attack({"waf_data": ret.data})
            if ret.action == waf.PW_BLOCK and self.block is True:
                return {"status": "raise", "rule_name": self.rule_name}
        elif ret.action < 0:
            raise RuntimeError("WAF returned unexpected action: %r", ret)

    @staticmethod
    def module_is_available():
        """ Return True if the native module is present, False otherwise.
        """
        return waf is not None
