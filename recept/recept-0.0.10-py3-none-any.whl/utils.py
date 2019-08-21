import re

__FIRST_CAP_RE = re.compile(r"(.)([A-Z][a-z]+)")
__ALL_CAP_RE = re.compile(r"([a-z0-9])([A-Z])")
__FORBIDDEN_CHARS_RE = re.compile(r"[^\w]+")


def camel_case_to_snake_case(s: str, sep: str = "_") -> str:
    """Convert camel case to snake case.

    Args:
        s (str): String that should be converted to snake case.
        sep (str): Separator. Default is ``_`` so the final string will look
            like ``some_snake_case_string``, but we can pass ``-`` and then the
            result will be ``some-kebab-case-string``.
    """
    s1 = __FORBIDDEN_CHARS_RE.sub(sep, s)
    s2 = __FIRST_CAP_RE.sub(rf"\1{sep}\2", s1)
    return __ALL_CAP_RE.sub(rf"\1{sep}\2", s2).lower()
