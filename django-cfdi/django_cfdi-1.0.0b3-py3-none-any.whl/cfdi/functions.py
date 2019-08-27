import math
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone
from importlib import import_module
import datetime

def to_decimal(s):
    """
    Docs.
    """
    try:
        s = str(s)
        s = s.replace("$", "")
        d = Decimal("".join(s.split(",")))
        return d if not math.isnan(d) else 0
    except:
        return Decimal("0")


def to_int(s):
    """
    Docs.
    """
    try:
        return int(s)
    except:
        return 0


def to_precision_decimales(valor_decimal, precision=2):
    """
    Docs.
    """
    if not valor_decimal:
        return Decimal("0.00")
    return Decimal("%s" % valor_decimal).quantize(
        Decimal("0.%0*d" % (precision, 1)), ROUND_HALF_UP
    )


def to_datetime(date, max=False, use_localtime=True, min=False):
    """
    Convierte un datetime naive en aware.
    """
    if max and min:
        raise ValueError(
            u"Los argumentos max y min deben ser mutuamente excluyentes"
        )

    if hasattr(date, "tzinfo") and date.tzinfo and not min and not max:
        return date

    if not isinstance(date, (datetime.date, datetime.datetime)):
        return date

    dt = datetime.datetime
    current_tz = timezone.get_current_timezone() if use_localtime else pytz.utc

    t = dt.min.time()

    # si date es datetime conservamos la hora que trae
    if not min and isinstance(date, (datetime.datetime,)):
        t = date.time()

    if max:
        t = dt.max.time()

    if settings.USE_TZ:
        return current_tz.localize(dt.combine(date, t))

    return timezone.localtime(dt.combine(date, t))

def load_func(func_path):
    """
    Retorna la funcion segun el path especificado, ej:
    cfdi.utils.load_func
    """
    package, module = func_path.rsplit('.', 1)
    return getattr(import_module(package), module)