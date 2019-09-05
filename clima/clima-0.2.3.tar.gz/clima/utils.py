def filter_fields(d: dict, nt):
    """Excludes fields not found in the schema/namedtuple"""
    res = {}
    for k, v in d.items():
        if k in nt._fields:
            res.update({k: v})

    return res


def type_correct_with(cdict, cfg_tuple):
    """Use type hints of the cfg tuple to cast variables into their intended types"""
    # TODO: This would be cleaner, if the config would use Schema or derivative in the
    # first place and use its validation process
    res = {}
    for k, v in cdict.items():
        res.update({k: type(getattr(cfg_tuple, k))(v)})
    return res
