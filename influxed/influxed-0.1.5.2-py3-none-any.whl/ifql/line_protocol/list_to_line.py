from influxed.ifql.line_protocol.dict_to_line import dict_to_line_protocol


def to_lines(list_, measurement):
    res = [dict_to_line_protocol(dict_, measurement) for dict_ in list_]
    return [x for x in res if x is not None]