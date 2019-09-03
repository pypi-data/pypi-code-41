# STDLIB
import datetime
from decimal import Decimal
from math import log
from typing import List, SupportsFloat, SupportsInt, Union

# OWN
import lib_regexp


def cast_float_2_string(value: Union[Decimal, float], n_stellen: int = 12, n_nachkommastellen: int = 2,
                        s_comma_seperator: str = ',') -> str:
    """
    decimal --> string

    >>> assert cast_float_2_string(100000.52) == '   100000,52'

    """
    s_value = ('{value:' + str(n_stellen) + '.' + str(n_nachkommastellen) + 'f}').format(value=value)
    s_value = s_value.replace('.', s_comma_seperator)
    return s_value


def cast_float_to_human_readable_size(value: Union[Decimal, float, int], s_unit: str = 'Byte', n_decimals: int = 2,
                                      b_base1024: bool = False, b_short_form: bool = False,
                                      b_remove_trailing_zeros: bool = False, b_show_multiplicator: bool = True) -> str:
    """
    formatiere große Zahlen in Human Readable Format, dzt nur für Bytes

    IEC (2^n)
    Ki(Kibi 2^10), Mi(Mebi 2^20), Gi(Gibi 2^30) Ti(Tebi 2^40),
    Pi(Pebi 2^50), Ei(Exbi 2^60), Zi(Zebi 2^70), Yi(Yobi 2^80)
    SI (10^n)
    Y(Yotta 10^24), Z(Zetta 10^21), E(Exa 10^18), P(Peta 10^15), T(Tera 10^12),G(Giga 10^9), M(Mega 10^6), k(kilo 10^3)

    :param value:                   der Wert
    :param s_unit:                  Einheit, z.Bsp. Byte, Sekunden ...
    :param n_decimals:              Anzahl der Dezimalstellen für Retourwert
    :param b_base1024:              wenn True ist der Multiplikator 1024, wenn false dann 1000
    :param b_short_form:            Kurzform : kByte statt KiloByte
    :param b_remove_trailing_zeros: Kommazahlen unterdrücken wenn Null : 1024 kByte statt 1024.00 kByte
    :param b_show_multiplicator:    Multiplikator anzeigen : '10.00 MilliVolt (x10^-3)'
    :return:  String


    >>> cast_float_to_human_readable_size(0.1,'Volt')
    '100.00 MilliVolt (x10^-3)'
    >>> cast_float_to_human_readable_size(0.01,'Volt')
    '10.00 MilliVolt (x10^-3)'
    >>> cast_float_to_human_readable_size(0.001,'Volt')
    '1.00 MilliVolt (x10^-3)'
    >>> cast_float_to_human_readable_size(0.000001,'Volt')
    '1.00 MikroVolt (x10^-6)'
    >>> cast_float_to_human_readable_size(0.000000001,'Volt')
    '1.00 NanoVolt (x10^-9)'
    >>> cast_float_to_human_readable_size(0.000000000001,'Volt')
    '1.00 PikoVolt (x10^-12)'
    >>> cast_float_to_human_readable_size(0.000000000000001,'Volt')
    '1.00 FemtoVolt (x10^-15)'
    >>> cast_float_to_human_readable_size(0.000000000000000001,'Volt')
    '1.00 AttoVolt (x10^-18)'
    >>> cast_float_to_human_readable_size(0.000000000000000000001,'Volt')
    '1.00 ZeptoVolt (x10^-21)'
    >>> cast_float_to_human_readable_size(0.000000000000000000000001,'Volt')
    '1.00 YoktoVolt (x10^-24)'
    >>> cast_float_to_human_readable_size(0.0000000000000000000000001,'Volt') # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    '0.10 YoktoVolt (x10^-24)'
    >>> cast_float_to_human_readable_size(0,'Volt')
    '0.00 Volt'
    >>> cast_float_to_human_readable_size(0,'Volt',b_remove_trailing_zeros=True)
    '0 Volt'
    >>> cast_float_to_human_readable_size(1,'Volt')
    '1.00 Volt'
    >>> cast_float_to_human_readable_size(1.00,'Volt')
    '1.00 Volt'
    >>> cast_float_to_human_readable_size(10,'Volt')
    '10.00 Volt'
    >>> cast_float_to_human_readable_size(100,'Volt')
    '100.00 Volt'
    >>> cast_float_to_human_readable_size(1000,'Volt')
    '1.00 KiloVolt (x10^3)'
    >>> cast_float_to_human_readable_size(1000000,'Volt')
    '1.00 MegaVolt (x10^6)'
    >>> cast_float_to_human_readable_size(1000000000,'Volt')
    '1.00 GigaVolt (x10^9)'
    >>> cast_float_to_human_readable_size(1000000000000,'Volt')
    '1.00 TeraVolt (x10^12)'
    >>> cast_float_to_human_readable_size(1000000000000000,'Volt')
    '1.00 PetaVolt (x10^15)'
    >>> cast_float_to_human_readable_size(1000000000000000000,'Volt')
    '1.00 ExaVolt (x10^18)'
    >>> cast_float_to_human_readable_size(1000000000000000000000,'Volt')
    '1.00 ZettaVolt (x10^21)'
    >>> cast_float_to_human_readable_size(1000000000000000000000000,'Volt')
    '1.00 YottaVolt (x10^24)'
    >>> cast_float_to_human_readable_size(1000000000000000000000000000,'Volt')
    '1000.00 YottaVolt (x10^24)'


    >>> cast_float_to_human_readable_size(1.00,'Volt',b_remove_trailing_zeros=True)
    '1 Volt'
    >>> cast_float_to_human_readable_size(1.5)
    '1.50 Byte'
    >>> cast_float_to_human_readable_size(12.3789,n_decimals=0)
    '12 Byte'
    >>> cast_float_to_human_readable_size(12.3789)
    '12.38 Byte'
    >>> cast_float_to_human_readable_size(1024,b_base1024=True)
    '1 KibiByte (x1024^1)'
    >>> cast_float_to_human_readable_size(65535,b_base1024=True)
    '64 KibiByte (x1024^1)'
    >>> cast_float_to_human_readable_size(-3456,b_base1024=True)
    '-3 KibiByte (x1024^1)'
    >>> cast_float_to_human_readable_size(0.1,b_base1024=True)
    '0 Byte'
    >>> cast_float_to_human_readable_size(-0.1,b_base1024=True)
    '0 Byte'

    """

    value = float(value)
    # handling für negative Zahlen - Absolutwert verwenden und in der Ausgabe '-' hinzufügen
    b_negative = False
    if value < 0:
        b_negative = True
        value = value * -1

    n_factor = 1000         # Basis for Log
    n_list_index_add = 8      # Position der Liste für value 1...999 , also kein prefix

    # bei IEC Prefix, keine Kommazahlen, keine Dezimalstellen anzeichen
    if b_base1024:
        value = round(value, 0)           # keine Kommazahlen für Base 1024
        b_remove_trailing_zeros = True    # keine trailing Zeros
        n_decimals = 0                    # keine Nachkommastellen, Runden auf 1 Stelle
        n_factor = 1024                 # basis 1024
        n_list_index_add = 0            # Die Liste für Basis 1024 startet mit 0

    # handling für Null, denn log von 0 geht nicht
    if value == 0:
        if b_remove_trailing_zeros:
            s_result = '0 ' + s_unit
        else:
            s_format = '{:.%sf} ' % n_decimals  # format String
            s_result = s_format.format(0) + s_unit
        return s_result

    if b_base1024:          # IEC Prefixe (2**n)
        lst_prefix = [('', '', ''),
                      ('Ki', 'Kibi', ' (x1024^1)'),
                      ('Mi', 'Mebi', ' (x1024^2)'),
                      ('Gi', 'Gibi', ' (x1024^3)'),
                      ('Ti', 'Tebi', ' (x1024^4)'),
                      ('Pi', 'Pebi', ' (x1024^5)'),
                      ('Ei', 'Exbi', ' (x1024^6)'),
                      ('Zi', 'Zebi', ' (x1024^7)'),
                      ('Yi', 'Yobi', ' (x1024^8)')]

    else:       # ISO Prefixe (10**n)
        lst_prefix = [('y', 'Yokto', ' (x10^-24)'),
                      ('z', 'Zepto', ' (x10^-21)'),
                      ('a', 'Atto', ' (x10^-18)'),
                      ('f', 'Femto', ' (x10^-15)'),
                      ('p', 'Piko', ' (x10^-12)'),
                      ('n', 'Nano', ' (x10^-9)'),
                      ('µ', 'Mikro', ' (x10^-6)'),
                      ('m', 'Milli', ' (x10^-3)'),
                      ('', '', ''),
                      ('k', 'Kilo', ' (x10^3)'),
                      ('M', 'Mega', ' (x10^6)'),
                      ('G', 'Giga', ' (x10^9)'),
                      ('T', 'Tera', ' (x10^12)'),
                      ('P', 'Peta', ' (x10^15)'),
                      ('E', 'Exa', ' (x10^18)'),
                      ('Z', 'Zetta', ' (x10^21)'),
                      ('Y', 'Yotta', ' (x10^24)')]

    exponent = log(value, n_factor)
    if value < 1:
        exponent = exponent - 1
        # sonst bekommen wir bei value=0.001  1000 Mikro statt 1 Milli is_int funktioniert hier nicht
        if int(exponent) == exponent:
            exponent = exponent + 1      # da log immer float gibt - daher if int(exponent) == exponent
    exponent = int(exponent)

    if exponent < -8:  # wenn kleiner als yokto 10^-24, dann trotzdem in yokto angeben
        exponent = -8

    if exponent > 8:  # wenn grösser als Yotta 10^24, dann trotzdem in Yotta angeben
        exponent = 8

    quotient = value / n_factor ** exponent

    n_index = exponent + n_list_index_add

    s_short_prefix, s_prefix, s_mul = lst_prefix[n_index]
    if b_short_form:
        s_prefix = s_short_prefix

    f_ret_val = round(quotient, n_decimals)     # auf gewünschte Stellen runden
    s_format = '{:.%sf}' % n_decimals           # format String
    s_ret_val = s_format.format(f_ret_val)      # Zahlenwert nun als String

    if b_negative:
        s_ret_val = '-' + s_ret_val

    if b_remove_trailing_zeros and n_decimals > 0:
        s_ret_val = s_ret_val.rstrip('0').rstrip('.')

    s_ret_val = s_ret_val + ' ' + s_prefix + s_unit
    if b_show_multiplicator:
        s_ret_val = s_ret_val + s_mul

    return s_ret_val


def cast_float_2_human_readable_timediff(float_seconds: Union[Decimal, float], language: str = 'de') -> str:
    """
    dient dazu Laufzeiten von Programmen gerundet in einem lesbaren Format anzuzeigen

    >>> cast_float_2_human_readable_timediff(89452.456898418)
    '  1 Tage,  0 Stunden, 50 Minuten, 52 Sekunden'
    >>> cast_float_2_human_readable_timediff(86572.456898418)
    '  1 Tage,  0 Stunden,  2 Minuten, 52 Sekunden'
    >>> cast_float_2_human_readable_timediff(7600.456898418)
    ' 2 Stunden,  6 Minuten, 40 Sekunden'
    >>> cast_float_2_human_readable_timediff(2455.456898418)
    '40 Minuten, 55 Sekunden'
    >>> cast_float_2_human_readable_timediff(955.456898418)
    '15 Minuten, 55 Sekunden'
    >>> cast_float_2_human_readable_timediff(155.456898418)
    ' 2 Minuten, 35 Sekunden'
    >>> cast_float_2_human_readable_timediff(52.456898418)
    '52.5 Sekunden'
    >>> cast_float_2_human_readable_timediff(8.456898418)
    '8.46 Sekunden'
    >>> cast_float_2_human_readable_timediff(2.456898418)
    '2.46 Sekunden'
    >>> cast_float_2_human_readable_timediff(0.456898418)
    '457 ms'
    >>> cast_float_2_human_readable_timediff(0.056898418)
    '56.9 ms'
    >>> cast_float_2_human_readable_timediff(0.006898418)
    '6.90 ms'
    >>> cast_float_2_human_readable_timediff(0.000898418)
    '898 µs'
    >>> cast_float_2_human_readable_timediff(0.000098418)
    '98.4 µs'
    >>> cast_float_2_human_readable_timediff(0.000008418)
    '8.42 µs'
    >>> cast_float_2_human_readable_timediff(0.000000418)
    '418 ns'
    >>> cast_float_2_human_readable_timediff(0.0000000418)
    '42 ns'
    >>> cast_float_2_human_readable_timediff(0.00000000418)
    '4 ns'
    >>> cast_float_2_human_readable_timediff(0.00000000498)
    '5 ns'
    >>> cast_float_2_human_readable_timediff(0.000000000418)
    '0 ns'
    """

    language_lower = language.lower()

    hash_tag_days_by_language = dict()
    hash_tag_hours_by_language = dict()
    hash_tag_minutes_by_language = dict()
    hash_tag_seconds_by_language = dict()

    hash_tag_days_by_language['de'] = 'Tage'
    hash_tag_days_by_language['en'] = 'days'
    hash_tag_hours_by_language['de'] = 'Stunden'
    hash_tag_hours_by_language['en'] = 'hours'
    hash_tag_minutes_by_language['de'] = 'Minuten'
    hash_tag_minutes_by_language['en'] = 'minutes'
    hash_tag_seconds_by_language['de'] = 'Sekunden'
    hash_tag_seconds_by_language['en'] = 'seconds'

    tag_days = hash_tag_days_by_language[language_lower]
    tag_hours = hash_tag_hours_by_language[language_lower]
    tag_minutes = hash_tag_minutes_by_language[language_lower]
    tag_seconds = hash_tag_seconds_by_language[language_lower]

    n_days, f_remainder = divmod(float_seconds, 86400)
    n_hours, f_remainder = divmod(f_remainder, 3600)
    n_minutes, f_remainder = divmod(f_remainder, 60)
    f_seconds = f_remainder
    f_milliseconds = f_seconds * 1000
    f_microseconds = f_seconds * 1000000
    f_nanoseconds = f_seconds * 1000000000

    n_days = int(n_days)
    n_hours = int(n_hours)
    n_minutes = int(n_minutes)

    if n_days > 0:
        s_timediff_de = '{:3.0f} {tag_days}, {:2.0f} {tag_hours}, {:2.0f} {tag_minutes}, {:2.0f} {tag_seconds}'\
            .format(n_days, n_hours, n_minutes, f_seconds,
                    tag_days=tag_days, tag_hours=tag_hours, tag_minutes=tag_minutes, tag_seconds=tag_seconds)

    elif n_hours > 0:
        s_timediff_de = '{:2.0f} {tag_hours}, {:2.0f} {tag_minutes}, {:2.0f} {tag_seconds}'\
            .format(n_hours, n_minutes, f_seconds,
                    tag_hours=tag_hours, tag_minutes=tag_minutes, tag_seconds=tag_seconds)
    elif n_minutes > 0:
        s_timediff_de = '{:2.0f} {tag_minutes}, {:2.0f} {tag_seconds}'\
            .format(n_minutes, f_seconds, tag_minutes=tag_minutes, tag_seconds=tag_seconds)

    # grösser gleich 10 Sekunden : eine Kommastelle anzeigen , z.Bsp 12.4 Sekunden
    elif f_seconds >= 10:
        s_timediff_de = '{:2.1f} {tag_seconds}'.format(f_seconds, tag_seconds=tag_seconds)
    # grösser 1 Sekunde : zwei Kommastellen anzeigen , z.Bsp 8.43 Sekunden
    elif f_seconds >= 1:
        s_timediff_de = '{:1.2f} {tag_seconds}'.format(f_seconds, tag_seconds=tag_seconds)
    # grösser gleich 100ms : keine Kommastellen anzeigen , z.Bsp 214 ms
    elif f_milliseconds >= 100:
        s_timediff_de = '{:3.0f} ms'.format(f_milliseconds)
    # grösser gleich 10ms : eine Kommastellen anzeigen , z.Bsp 64,5 ms
    elif f_milliseconds >= 10:
        s_timediff_de = '{:2.1f} ms'.format(f_milliseconds)
    # grösser gleich 1ms : zwei Kommastellen anzeigen , z.Bsp 4,53 ms
    elif f_milliseconds >= 1:
        s_timediff_de = '{:1.2f} ms'.format(f_milliseconds)
    # grösser gleich 100µs : keine Kommastellen anzeigen , z.Bsp 243 µs
    elif f_microseconds >= 100:
        s_timediff_de = '{:3.0f} µs'.format(f_microseconds)
    # grösser gleich 10µs : eine Kommastellen anzeigen , z.Bsp 24.3 µs
    elif f_microseconds >= 10:
        s_timediff_de = '{:2.1f} µs'.format(f_microseconds)
    # grösser gleich 1µs : zwei Kommastellen anzeigen , z.Bsp 4.32 µs
    elif f_microseconds >= 1:
        s_timediff_de = '{:1.2f} µs'.format(f_microseconds)
    # grösser gleich 100 ns keine Kommastellen angeben, z.Bsp. 243 ns
    elif f_nanoseconds >= 100:
        s_timediff_de = '{:3.0f} ns'.format(f_nanoseconds)
    # grösser gleich 10 ns keine Kommastellen angeben, z.Bsp. 24 ns
    elif f_nanoseconds >= 10:
        s_timediff_de = '{:2.0f} ns'.format(f_nanoseconds)
    # grösser gleich 1 ns keine Kommastellen angeben, z.Bsp. 9 ns
    elif f_nanoseconds >= 1:
        s_timediff_de = '{:1.0f} ns'.format(f_nanoseconds)
    # kleiner 1 ns keine Kommastellen angeben, z.Bsp. 0 ns
    else:
        s_timediff_de = '{:1.0f} ns'.format(f_nanoseconds)
    return s_timediff_de


def cast_float_2_human_readable_dimension(dimension_in_meters: Union[Decimal, float], language: str = 'de', unit_short: bool = True) -> str:
    """
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('9876.987654'))
    '9.88 km'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('876.987654'))
    '877 m'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('76.987654'))
    '77.0 m'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('6.987654'))
    '6.99 m'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('0.987654'))
    '988 mm'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('0.087654'))
    '88 mm'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('0.007654'))
    '7.65 mm'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('0.000654'))
    '0.654 mm'
    >>> cast_float_2_human_readable_dimension(dimension_in_meters=Decimal('0.000054'))
    '54.0 µm'
    """
    language = language.lower()
    dict_m = {True: {'de': 'm', 'en': 'm'}, False: {'de': 'Meter', 'en': 'meters'}}
    dict_mm = {True: {'de': 'mm', 'en': 'mm'}, False: {'de': 'Millimeter', 'en': 'millimeter'}}
    dict_um = {True: {'de': 'µm', 'en': 'µm'}, False: {'de': 'Mikrometer', 'en': 'micrometer'}}

    if dimension_in_meters >= 1000:
        dict_km = {True: {'de': 'km', 'en': 'km'}, False: {'de': 'Kilometer', 'en': 'kilometer'}}
        dimension_in_kilometers = dimension_in_meters / 1000
        s_dimension = "{0:.2f} ".format(dimension_in_kilometers) + dict_km[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 100:
        s_dimension = "{0:.0f} ".format(dimension_in_meters) + dict_m[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 10:
        s_dimension = "{0:.1f} ".format(dimension_in_meters) + dict_m[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 1:
        s_dimension = "{0:.2f} ".format(dimension_in_meters) + dict_m[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 0.010:
        dimension_in_mm = dimension_in_meters * 1000
        s_dimension = "{0:.0f} ".format(dimension_in_mm) + dict_mm[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 0.001:
        dimension_in_mm = dimension_in_meters * 1000
        s_dimension = "{0:.2f} ".format(dimension_in_mm) + dict_mm[unit_short][language]
        return s_dimension
    elif dimension_in_meters >= 0.0001:
        dimension_in_mm = dimension_in_meters * 1000
        s_dimension = "{0:.3f} ".format(dimension_in_mm) + dict_mm[unit_short][language]
        return s_dimension
    else:
        dimension_in_um = dimension_in_meters * 1000000
        s_dimension = "{0:.1f} ".format(dimension_in_um) + dict_um[unit_short][language]
        return s_dimension


def cast_float_2_human_readable_iterations(float_seconds: Union[Decimal, float]) -> str:
    """
    >>> cast_float_2_human_readable_iterations(42328.123456789)
    '2.04 Iterationen pro Tag'
    >>> cast_float_2_human_readable_iterations(3456.123456789)
    '1.04 Iterationen pro Stunde'
    >>> cast_float_2_human_readable_iterations(100.123456789)
    '35.96 Iterationen pro Stunde'
    >>> cast_float_2_human_readable_iterations(32.123456789)
    '1.87 Iterationen pro Minute'
    >>> cast_float_2_human_readable_iterations(0.123456789)
    '8.10 Iterationen pro Sekunde'
    >>> cast_float_2_human_readable_iterations(0.0123456789)
    '81 Iterationen pro Sekunde'
    >>> cast_float_2_human_readable_iterations(0.00023158)
    '4318 Iterationen pro Sekunde'
    >>> cast_float_2_human_readable_iterations(0.00000158)
    '632911 Iterationen pro Sekunde'
    >>> cast_float_2_human_readable_iterations(0)
    '∞ pro Sekunde (nicht messbar)'

    """
    if float_seconds > 3600:
        s_iterations = '{iterations:2.2f} Iterationen pro Tag'.format(iterations=86400 / float_seconds)
    elif float_seconds > 60:
        s_iterations = '{iterations:2.2f} Iterationen pro Stunde'.format(iterations=3600 / float_seconds)
    elif float_seconds > 1:
        s_iterations = '{iterations:2.2f} Iterationen pro Minute'.format(iterations=60 / float_seconds)
    elif float_seconds > 0.02:
        s_iterations = '{iterations:1.2f} Iterationen pro Sekunde'.format(iterations=1 / float_seconds)
    elif float_seconds > 0:
        s_iterations = '{iterations:1.0f} Iterationen pro Sekunde'.format(iterations=1 / float_seconds)
    else:
        s_iterations = '∞ pro Sekunde (nicht messbar)'
    return s_iterations


def cast_float_2_human_readable_weight(weight_in_kg: Union[float, Decimal], language: str = 'de') -> str:
    """
    >>> cast_float_2_human_readable_weight(Decimal('1899.567'), language='de')
    '1.90 Tonnen'
    >>> cast_float_2_human_readable_weight(Decimal('1899.567'), language='en')
    '1.90 tons'
    >>> cast_float_2_human_readable_weight(Decimal('899.567'))
    '900 Kilogramm'
    >>> cast_float_2_human_readable_weight(Decimal('99.567'))
    '99.6 Kilogramm'
    >>> cast_float_2_human_readable_weight(Decimal('9.567'))
    '9.57 Kilogramm'
    >>> cast_float_2_human_readable_weight(Decimal('0.567'))
    '567 Gramm'
    >>> cast_float_2_human_readable_weight(Decimal('0.067'))
    '67 Gramm'
    >>> cast_float_2_human_readable_weight(Decimal('0.007'))
    '7 Gramm'
    >>> cast_float_2_human_readable_weight(1899.567, language='de')
    '1.90 Tonnen'

    """
    dict_kg = {'de': 'Kilogramm', 'en': 'kilogram'}
    language = language.lower()

    if weight_in_kg >= 1000:
        dict_tons = {'de': 'Tonnen', 'en': 'tons'}
        weight_in_tons = weight_in_kg / 1000
        s_weight = "{0:.2f} ".format(weight_in_tons) + dict_tons[language]
        return s_weight
    elif weight_in_kg >= 100:
        s_weight = "{0:.0f} ".format(weight_in_kg) + dict_kg[language]
        return s_weight
    elif weight_in_kg >= 10:
        s_weight = "{0:.1f} ".format(weight_in_kg) + dict_kg[language]
        return s_weight
    elif weight_in_kg >= 1:
        s_weight = "{0:.2f} ".format(weight_in_kg) + dict_kg[language]
        return s_weight
    else:
        dict_grams = {'de': 'Gramm', 'en': 'grams'}
        weight_in_gramm = weight_in_kg * 1000
        s_weight = "{0:.0f} ".format(weight_in_gramm) + dict_grams[language]
        return s_weight


def cast_human_readable_size_to_float(s_human_readable_size: Union[str, int, bool, float]) -> float:
    """
    IEC (2^n)
    Ki(Kibi 2^10), Mi(Mebi 2^20), Gi(Gibi 2^30) Ti(Tebi 2^40),
    Pi(Pebi 2^50), Ei(Exbi 2^60), Zi(Zebi 2^70), Yi(Yobi 2^80)

    SI (10^n)
    Y(Yotta 10^24), Z(Zetta 10^21), E(Exa 10^18), P(Peta 10^15), T(Tera 10^12),
    G(Giga 10^9), M(Mega 10^6), k(kilo 10^3), h(hekto 10^2),da(Deka 10^1),
    d(Dezi 10^-1), c(Zenti 10^-2), m(Milli 10^-3), u|µ(Mikro 10^-6), n(Nano 10^-9),
    p(Piko 10^-12), f(Femto 10^-15), a(Atto 10^-18), z(Zepto 10^-21), y(Yokto 10^-24)

    :param s_human_readable_size:  True: Hexadezimaler Multiplikator (1024),
                                   False : dezimaler Multiplikator (1000), default=True
    :return:                n_result, Wert als Integer oder Decimal

    >>> cast_human_readable_size_to_float('2GB')
    2000000000
    >>> cast_human_readable_size_to_float(5)
    5.0
    >>> cast_human_readable_size_to_float('-1')
    -1.0
    >>> cast_human_readable_size_to_float('0')
    0.0
    >>> cast_human_readable_size_to_float('1024 Byte')      # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: can not identify SI or IEC prefix 'Byte'

    >>> cast_human_readable_size_to_float('65000 byte')     # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: can not identify SI or IEC prefix 'byte'

    >>> cast_human_readable_size_to_float('10 Mb')
    10000000
    >>> cast_human_readable_size_to_float('5 Gb')
    5000000000
    >>> cast_human_readable_size_to_float('5.5 Gb')
    5500000000
    >>> cast_human_readable_size_to_float('5.5 GiByte')
    5905580032
    >>> cast_human_readable_size_to_float('5.5 useconds')
    5.5e-06
    >>> cast_human_readable_size_to_float('5.5 milliseconds')
    0.0055
    >>> cast_human_readable_size_to_float(True)
    1.0
    >>> cast_human_readable_size_to_float(False)
    0.0

    """

    # wenn die Größe keine Instanz von String, so unverändert retour geben.
    if not isinstance(s_human_readable_size, str):
        return float(s_human_readable_size)

    # suche den ersten buchstaben a-ze
    n_position, s_first_letter_found = lib_regexp.regexp_check_chars_azAZ.search(s_human_readable_size)

    result = float(s_human_readable_size[:n_position])

    if n_position is None:
        return result

    s_prefix = s_human_readable_size[n_position:]

    lst_prefixe = [('Ki', 'Kibi', 2**10),
                   ('Mi', 'Mebi', 2**20),
                   ('Gi', 'Gibi', 2**30),
                   ('Ti', 'Tebi', 2**40),
                   ('Pi', 'Pebi', 2**50),
                   ('Ei', 'Exbi', 2**60),
                   ('Zi', 'Zebi', 2**70),
                   ('Yi', 'Yobi', 2**80),
                   ('Y', 'Yotta', 1E24),
                   ('Z', 'Zetta', 1E21),
                   ('E', 'Exa', 1E18),
                   ('P', 'Peta', 1E15),
                   ('T', 'Tera', 1E12),
                   ('G', 'Giga', 1E9),
                   ('M', 'Mega', 1E6),
                   ('k', 'kilo', 1E3),
                   ('h', 'hekto', 1E2),
                   ('da', 'Deka', 10),
                   ('d', 'Dezi', 1E-1),
                   ('c', 'Zenti', 1E-2),
                   ('m', 'Milli', 1E-3),
                   ('u', 'Mikro', 1E-6),
                   ('µ', 'Mikro', 1E-6),
                   ('n', 'Nano', 1E-9),
                   ('p', 'Piko', 1E-12),
                   ('f', 'Femto', 1E-15),
                   ('a', 'Atto', 1E-18),
                   ('z', 'Zepto', 1E-21),
                   ('y', 'Yokto', 1E-24)
                   ]

    for (s_pref, s_pref_name, dec_faktor) in lst_prefixe:
        if s_prefix.startswith(s_pref) or s_prefix.lower().startswith(s_pref_name.lower()):        # suche nach den ganzen Einheiten lowercase
            result = result * dec_faktor
            if int(result) == result:    # wenn möglich in int retournieren
                return int(result)
            else:
                return result

    raise ValueError("can not identify SI or IEC prefix '{}'".format(s_prefix))


def cast_to_bool(value: Union[str, int, bool, float, None]) -> bool:
    """
    >>> cast_to_bool('')
    False
    >>> cast_to_bool('j')
    True
    >>> cast_to_bool('n')
    False
    >>> cast_to_bool('1')
    True
    >>> cast_to_bool('0')
    False
    >>> cast_to_bool('0.0')
    False
    >>> cast_to_bool('2.0')
    True
    >>> cast_to_bool(False)
    False
    >>> cast_to_bool(True)
    True
    >>> cast_to_bool(1)
    True
    >>> cast_to_bool(1.0)
    True
    >>> cast_to_bool(0.0)
    False
    >>> cast_to_bool(None)
    False

    >>> cast_to_bool('xx')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    ValueError: Value "xx" cant be casted to bool


    """
    if isinstance(value, str):
        value = value.strip().lower()
    if not value:
        return False
    if value in ('j', 'ja', 'y', 'yes', 'true', 'wahr', '1'):
        return True
    elif value in ('n', 'no', 'nein', 'false', 'falsch', 'unwahr', 'none', '0'):
        return False
    elif is_castable_to_float(value):
        float_value = float(value)
        if float_value:
            return True
        else:
            return False
    else:
        raise ValueError('Value "{}" cant be casted to bool'.format(str(value)))


def cast_str_2_dec(s_value: str, s_comma_seperator: str = ',') -> Decimal:
    """
    string --> Decimal
    >>> assert cast_str_2_dec('100000,52') == Decimal('100000.52')
    """
    s_value = s_value.replace(s_comma_seperator, '.')
    dec_value = Decimal(s_value)
    return dec_value


def cast_str_2_list(s_input: str, keep_empty_list_items: bool = True, split_character: str = ',', strip_items: bool = True) -> List[str]:
    """
    >>> cast_str_2_list('a')
    ['a']
    >>> cast_str_2_list('a, b')
    ['a', 'b']
    >>> cast_str_2_list('a, b',strip_items=False)
    ['a', ' b']
    >>> cast_str_2_list('a, , b')
    ['a', '', 'b']
    >>> cast_str_2_list('a, , b', keep_empty_list_items=False)
    ['a', 'b']

    """
    raw_items = s_input.split(split_character)
    items = list()
    for raw_item in raw_items:
        if strip_items:
            raw_item = raw_item.strip()
        if raw_item:
            items.append(raw_item)
        elif keep_empty_list_items:
            items.append('')
    return items


def cast_list_of_strings_to_lower(list_of_strings: List[str]) -> List[str]:
    """
    >>> cast_list_of_strings_to_lower(['Abra','WhaT'])
    ['abra', 'what']
    """
    items = list()
    for string in list_of_strings:
        string = string.lower()
        items.append(string)
    return items


def get_type_as_string(instance: object) -> str:
    """
    >>> x='a'
    >>> get_type_as_string(x)
    'str'

    >>> x=1
    >>> get_type_as_string(x)
    'int'

    >>> import decimal
    >>> x=decimal.Decimal(1.00)
    >>> get_type_as_string(x)
    'Decimal'
    >>> x=[]
    >>> get_type_as_string(x)
    'list'

    """
    return type(instance).__name__


def is_castable_to_bool(value: Union[str, int, bool, float, None]) -> bool:
    """
    >>> is_castable_to_bool(True)
    True
    >>> is_castable_to_bool('xx')
    False
    >>> is_castable_to_bool('True')
    True
    >>> is_castable_to_bool('')
    True
    >>> is_castable_to_bool(None)
    True

    """

    try:
        cast_to_bool(value)
        return True
    except ValueError:
        return False


def is_castable_to_float(value: Union[SupportsFloat, str, bytes, bytearray]) -> bool:
    """
    prüft ob das objekt in float umgewandelt werden kann

    Argumente  : o_object    : der Wert der zu prüfen ist
    Returns    : True|False
    Exceptions : keine

    >>> is_castable_to_float(1)
    True
    >>> is_castable_to_float('1')
    True
    >>> is_castable_to_float('1.0')
    True
    >>> is_castable_to_float('1,0')
    False
    >>> is_castable_to_float('True')
    False
    >>> is_castable_to_float(True)
    True
    >>> is_castable_to_float('')
    False
    >>> is_castable_to_float(None)
    False

    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def is_castable_to_int(value: Union[str, bytes, SupportsInt]) -> bool:
    """
    >>> is_castable_to_int(1)
    True
    >>> is_castable_to_int('1')
    True
    >>> is_castable_to_int('1.0')
    False
    >>> is_castable_to_int('1,0')
    False
    >>> is_castable_to_int('True')
    False
    >>> is_castable_to_int(True)
    True
    >>> is_castable_to_int('')
    False
    >>> is_castable_to_int(None)
    False

    """
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def cast_datetime_2_str(d_datetime: datetime.datetime, b_format_for_filename: bool = False) -> str:
    """
    Konvertiere datetime auf String im Format yyyy-mm-dd hh:mm:ss
    oder zur Verwendung in File- oder Verzeichnisnamen als String yyyy-mm-dd_hh-mm-ss

    >>> # gibt z.Bsp.: '2017-11-08_13-10-57'
    >>> dt = datetime.datetime.now()
    >>> cast_datetime_2_str(dt,True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    '...-...-..._...-...-...'

    >>> # gibt z.Bsp.: '2017-11-08 13:10:57'
    >>> cast_datetime_2_str(dt)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    '...-...-...:...:...'

    """

    s_datetime = d_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if b_format_for_filename:
        s_datetime = s_datetime.replace(':', '-')
        s_datetime = s_datetime.replace(' ', '_')                    # 2015-06-06_17-21-02
    return s_datetime


def cast_str_2_datetime(s_datetime: str, b_format_for_filename: bool = False) -> datetime.datetime:
    """
    konvertiere String im Format yyyy-mm-dd hh:mm:ss in datetime.datetime Format
    oder bei Verwendung von  b_format_for_filename String yyyy-mm-dd_hh-mm-ss in datetime.datetime Format

    >>> cast_str_2_datetime('2018-07-01 12:00:00')
    datetime.datetime(2018, 7, 1, 12, 0)
    >>> cast_str_2_datetime('2018-07-01_12-00-00', b_format_for_filename=True)
    datetime.datetime(2018, 7, 1, 12, 0)

    """

    if b_format_for_filename:
        s_datetime_date, s_datetime_time = s_datetime.split('_')
        s_datetime_time = s_datetime_time.replace('-', ':')
        s_datetime = s_datetime_date + ' ' + s_datetime_time

    s_date, s_time = s_datetime.split(' ')
    s_year, s_month, s_day = s_date.split('-')
    n_year = int(s_year)
    n_month = int(s_month)
    n_day = int(s_day)
    s_hour, s_minute, s_second = s_time.split(':')
    n_hour = int(s_hour)
    n_minute = int(s_minute)
    n_second = int(s_second)
    d_datetime = datetime.datetime(n_year, n_month, n_day, n_hour, n_minute, n_second)
    return d_datetime
