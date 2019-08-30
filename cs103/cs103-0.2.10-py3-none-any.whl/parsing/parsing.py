from typing import Optional

def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None

def parse_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except ValueError:
        return None

def parse_bool(s: str) -> Optional[bool]:
    if len(s) == 0:
        return None
    if s == "0" || s.lower() == "false":
        return False
    return True
