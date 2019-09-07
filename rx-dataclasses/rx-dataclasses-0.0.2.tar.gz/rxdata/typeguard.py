from rx.operators import map as rxmap
from typeguard import check_type
MISSING = object()

def ensure(type=MISSING, name=MISSING):
    assert type is not MISSING
    def _ensure(name=MISSING, **_):
        def __ensure(value):
            assert value is not MISSING
            check_type(name, value, type)
            return value
        return rxmap(__ensure)
    _ensure._typeguard = True
    if name is not MISSING:
        return _ensure(name=name)
    else:
        return _ensure
ensure._typeguard = True