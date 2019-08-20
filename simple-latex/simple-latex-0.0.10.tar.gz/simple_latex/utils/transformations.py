import re

def transform_dict_to_kv_list(options):
    """
    {"key": None, "key2": None} becomes 'key, key2'
    {"key": "\"\"", "key2": "3.5in", tocbibind: None} becomes 'key="", key2=3.5in, tocbibind'
    """
    assert isinstance(options, dict)
    return ", ".join(["{}={}".format(k,v) if v is not None else k for k,v in options.items()])

regex_non_escaped_bslash = r"(?<!\\)\\(?=(?:\\\\)*(?!\\)(?![\^\$#{}%~]))" # unescaped backslash
regex_non_escaped_carrot = r"(?<!\\)\^"
regex_non_escaped_dollar = r"(?<!\\)\$"
regex_non_escaped_hash = r"(?<!\\)#"
regex_non_escaped_lbracket = r"(?<!\\){"
regex_non_escaped_percent = r"(?<!\\)%(?!\\n)" # percent not followed directly by a \n
regex_non_escaped_rbracket = r"(?<!\\)}"
regex_non_escaped_tilde = r"(?<!\\)~"
regex_non_escaped_underscore = r"(?<!\\)_"
def latex_escape_regular_text(value):
    temp_value = value
    temp_value = re.sub(regex_non_escaped_rbracket, "\\}", temp_value)
    temp_value = re.sub(regex_non_escaped_lbracket, "\\{", temp_value)
    temp_value = re.sub(regex_non_escaped_bslash, "\\textbackslash{}", temp_value)
    temp_value = re.sub(regex_non_escaped_carrot, "\\^{}", temp_value)
    temp_value = re.sub(regex_non_escaped_dollar, "\\$", temp_value)
    temp_value = re.sub(regex_non_escaped_hash, "\\#", temp_value)
    temp_value = re.sub(regex_non_escaped_percent, "\\%", temp_value)
    temp_value = re.sub(regex_non_escaped_tilde, "\\~", temp_value)
    temp_value = re.sub(regex_non_escaped_underscore, "\\_", temp_value)
    return temp_value
