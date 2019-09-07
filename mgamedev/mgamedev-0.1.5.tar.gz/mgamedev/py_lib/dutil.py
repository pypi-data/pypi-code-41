# encoding:utf8

'''
Code for xl-tool helper functions!
'''
import os
import json
import logging
logging.basicConfig(level=logging.INFO)

KERROR_OPENCFG = {
    "open_failed": "Target cfgfile read failed!",
    "decode_failed": "Cfgfile decode error!",
    "keynot_exist": "Must set param not satisfy!"
}


def raise_error(codek):
    str_err = KERROR_OPENCFG.get(codek)
    logging.error(str_err)
    return (False, str_err)


class DUtil(object):
    @staticmethod
    def get_xlcfg(cfgfile, **kwads):
        strcfg = None
        try:
            with open(cfgfile, "r") as fp:
                strcfg = fp.read()
                fp.close()
        except IOError as identifier:
            logging.debug(identifier)
            return raise_error("open_failed")

        try:
            cfgdic = json.loads(strcfg)
        except (TypeError, ValueError) as identifier:
            logging.debug(identifier)
            return raise_error("decode_failed")

        if kwads.has_key("limitks") > 0:
            for k, _ in cfgdic.items():
                if k not in kwads.get("limitks"):
                    return raise_error("keynot_exist")
        return (True, cfgdic)


__all__ = [
    "DUtil"
]