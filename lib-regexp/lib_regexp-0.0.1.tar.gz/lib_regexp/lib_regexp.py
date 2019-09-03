# STDLIB
import re
from typing import List, Tuple, Union

try:
    from re import RegexFlag        # type: ignore      # for python 3.5
except ImportError:
    re.RegexFlag = int              # type: ignore


class ClassRegexExecute(object):
    """
    Führe eine regexp Suche oder Match durch
    Die Suche wird vorkompiliert abgespeichert.

    diese Klasse steht ganz oben in der Bibliothek, damit wir die vordefinierten Suchen in späteren Klassen verwenden können.

    Initialisierung:
    my_regexp=CRegex_execute(s_regexp)


    Parameter :     s_regexp            : ein Regexp String der die zu enthaltenden Zeichen beschreibt, z.Bsp: "[^a-z0-9.-]"
                                          die Suche ist Case Sensitive, somit würde ein Großbuchstabe ein unerlaubter Character sein
    Returns   :     mysearch            : ein Suchobjekt

    s_regexp Beispiele :
    [^a-z0-9.-]                         : Suche Zeichen die NICHT (^) a-z. 0-9,.,- enthalten
    \\d                                  : Suche erste Ziffer
    (?:aaa|bbb)                         : Suche String aaa,bbb in Searchstring

                                          Bsp. s_regext aus einer Liste mit Strings erzeugen :
                                          s_regexp = '(?:%s)' % '|'.join(ls_searchstrings)

    Methoden:

    SEARCH :
    n_position,s_found=my_regexp.search(s_string)

    Parameter :    s_string             : der zu durchsuchende String
    Returns   :    n_position           : die Position an welcher der erste Character gefunden wurde der hier nicht sein sollte, oder None
                   s_found              : der Character der nicht enthalten sein sollte, oder None

    MATCH:
    n_position,s_found=my_regexp.match(s_string)

    >>> # Characters finden die nicht enthalten sein dürfen
    >>> my_regexp=ClassRegexExecute('[^a-z0-9.-]')
    >>> my_regexp.search('sadfkjhstr1kljhsadfstr2')
    (None, None)
    >>> my_regexp.search('blkmnÜat1')
    (5, 'Ü')
    >>> my_regexp.search('sadfkjhstTrxkljhsadfstry')
    (9, 'T')

    >>> # Liste of Strings in einem String finden (erstes vorkommen)
    >>> s_regexp='(?:%s)' % '|'.join(['str1','str2'])
    >>> my_regexp.set_s_regexp(s_regexp)
    >>> my_regexp.search('sadfkjhstr1kljhsadfstr2')
    (7, 'str1')
    >>> my_regexp.search('sadfkjhstrxkljhsadfstry')
    (None, None)
    >>> s_regexp='(?:%s)' % '|'.join(['.jpg','.tif','\\.bat'])
    >>> my_regexp.set_s_regexp(s_regexp)
    >>> my_regexp.search('sadfkjhstr.jpgxkljhsadfstry')
    (10, '.jpg')
    >>> my_regexp.search('sadfkjhstrjp.batxkljhsadfstry')
    (12, '.bat')

    >>> # erstes Vorkommen einer Ziffer finden
    >>> my_regexp.set_s_regexp('\\d')
    >>> my_regexp.search('sadfkjhstr1kljhsadfstr2')
    (10, '1')
    >>> my_regexp.search('bat1')
    (3, '1')
    >>> my_regexp.search('sadfkjhstrxkljhsadfstry')
    (None, None)

    """

    def __init__(self, s_regexp: str = '', flags: Union[int, re.RegexFlag] = 0):
        self.my_regexp = re.compile(s_regexp, flags=flags)

    def set_s_regexp(self, s_regexp: str) -> None:
        self.my_regexp = re.compile(s_regexp)

    def search(self, s_string: str):                # type: ignore
        result = self.my_regexp.search(s_string)
        if result is None:
            return None, None
        else:
            return result.start(), result.group()

    def match(self, s_string: str):                # type: ignore
        result = self.my_regexp.match(s_string)
        if result is None:
            return None, None
        else:
            return result.start(), result.group()

    def findall(self, s_string: str):               # type: ignore
        result = self.my_regexp.findall(s_string)
        return result

    def sub(self, replace_with: str, s_input: str, count: int = 0):   # type: ignore
        result = self.my_regexp.sub(replace_with, s_input, count)
        return result


# VORDEFINIERTE REGEXP SUCHEN

# erstes Vorkommen einer Ziffer finden
regexp_ziffernsuche = ClassRegexExecute(r'\d')                                  # Ziffernsuche Instanz erzeugen, damit ist die Suche vorkompiliert

# Character finden a-z (case sensitive)
regexp_check_chars_az = ClassRegexExecute('[a-z]')                             # Instanz erzeugen, damit ist die Suche vorkompiliert
regexp_check_chars_azAZ = ClassRegexExecute('[a-zA-Z]')                        # Instanz erzeugen, damit ist die Suche vorkompiliert

# Alle Characters finden die nicht a-z,0-9,.,- sind (case sensitive)
regexp_check_chars_not_az09pointdash = ClassRegexExecute('[^a-z0-9.-]')        # Instanz erzeugen, damit ist die Suche vorkompiliert

# ^ = NOT
# \\w = Matches Unicode word characters; this includes most characters that can be part of a word in any language, as well as numbers and the underscore
# \s = Matches Unicode whitespace characters (which includes [ \t\n\r\f\v], and also many other characters,
# for example the non-breaking spaces mandated by typography rules in many languages
# regexp_non_standard_unicode_characters = ClassRegexExecute(r'[^\w\s\^°!"§$%&/\'\(\)\[\]{}\~€@\+\-\*\|\=\?\>\<,;\.:#²³©®¼½¾ª™øØ\\]', flags=re.UNICODE)
regexp_non_standard_unicode_characters = ClassRegexExecute(r'[^\w\s\^°!"§$%&/\'\(\)\[\]{}\~€@\+\-\*\|\=\?\>\<,;\.:#`²³©®¼½¾ª™øØ\\]', flags=re.UNICODE)


def reg_grep(pattern, text, pattern_is_regexp=False, flags=re.MULTILINE | re.UNICODE):
    # type: (str, str, bool, Union[int, re.RegexFlag]) -> List[str]
    # old  style type annotation because PEP8 E251 around flags: Union[int, re.RegexFlag] = re.MULTILINE | re.UNICODE

    """
    multiline grep

    # https://www.guru99.com/python-regular-expressions-complete-tutorial.html#5

    >>> assert reg_grep('a', 'this is a multiline\\nstring with some\\nmatching lines') == ['this is a multiline', 'matching lines']
    >>> assert reg_grep(r'^.*a.*$', 'this is a multiline\\nstring with some\\nmatching lines', pattern_is_regexp=True) ==\
            ['this is a multiline', 'matching lines']

    """
    if pattern_is_regexp:
        regexp_pattern = pattern
    else:
        regexp_pattern = r"^.*{pattern}.*$".format(pattern=pattern)

    l_results = re.findall(regexp_pattern, text, flags=flags)
    return l_results


def reg_is_str_in_text(pattern, text, flags=re.MULTILINE | re.UNICODE, pattern_is_regexp=False):
    # type: (str, str, Union[int, re.RegexFlag], bool) -> bool
    # old  style type annotation because PEP8 E251 around flags: Union[int, re.RegexFlag] = re.MULTILINE | re.UNICODE

    """
    multiline regexp search

    # https://www.guru99.com/python-regular-expressions-complete-tutorial.html#5

    >>> assert reg_is_str_in_text('a', 'this is a multiline\\nstring with some\\nmatching lines') == True
    >>> assert reg_is_str_in_text('matching', 'this is a multiline\\nstring with some\\nmatching lines') == True
    >>> assert reg_is_str_in_text('z', 'this is a multiline\\nstring with some\\nmatching lines') == False
    >>> assert reg_is_str_in_text(r"^.*a.*$", 'this is a multiline\\nstring with some\\nmatching lines', pattern_is_regexp=True) == True
    >>> assert reg_is_str_in_text(r"^.*matching.*$", 'this is a multiline\\nstring with some\\nmatching lines', pattern_is_regexp=True) == True
    >>> assert reg_is_str_in_text(r"^.*z.*$", 'this is a multiline\\nstring with some\\nmatching lines', pattern_is_regexp=True) == False

    """
    # line = re.search(r"^.*HEAD.*$", result.stdout, re.MULTILINE)

    if pattern_is_regexp:
        regexp_pattern = pattern
    else:
        regexp_pattern = r"^.*{pattern}.*$".format(pattern=pattern)

    match_object = re.search(regexp_pattern, text, flags=flags)
    if match_object:
        return True
    else:
        return False


def t_e_s_t_regexp(s_input: str) -> Tuple[str, List[str]]:
    """
    # named t_e_s_t_regexp that pytest does not automatically discover it as a fixture
    # bad‌​string  <-- ungültige (unsichtbare) unicode characters befinden in diesem string !!! diese sollen entfernt werden.
    >>> t_e_s_t_regexp('check_this_string_for_bad_characters^°!"§$%&/\\'()[]{}~€@öäüÖÄÜß+-*µ|><=?,;.:_ #²³©®¼½¾ª™øØ\\\\')
    ('check_this_string_for_bad_characters^°!"§$%&/\\'()[]{}~€@öäüÖÄÜß+-*µ|><=?,;.:_ #²³©®¼½¾ª™øØ\\\\', [])

    result = regexp_is_alphabetic_or_numeric.sub(input)
    return result


    """
    result = regexp_non_standard_unicode_characters.sub('', s_input)
    found = regexp_non_standard_unicode_characters.findall(s_input)
    return result, found
