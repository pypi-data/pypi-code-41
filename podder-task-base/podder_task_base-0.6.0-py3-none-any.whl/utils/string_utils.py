import re

KEBAB_CASE_PATTERN = '^[a-z0-9\-]{1,}$'


def is_kebab_case(text: str) -> bool:
    return bool(re.match(KEBAB_CASE_PATTERN, text))


def is_camel_case(text: str) -> bool:
    return text != text.lower() and text != text.upper() and "_" not in text


def to_snake_case(text: str) -> str:
    if is_kebab_case(text):
        return text.replace("-", "_")
    else:
        str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()


def to_kebab_case(text: str) -> str:
    return to_snake_case(text).replace("_", "-")


def to_camel_case(text: str) -> str:
    return ''.join(x.capitalize() or '_' for x in text.replace("_", "-").split('-'))


def to_env_var_case(text: str) -> str:
    return to_snake_case(text).upper()
