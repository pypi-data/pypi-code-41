import re
import sys
import unicodedata

xrange = range


def _charIsSep(aChar):
    return (
        not _charIsUpper(aChar)
        and not _charIsLower(aChar)
        and not _charIsNumberDecimalDigit(aChar)
    )


def _isSep(aString):
    return len(aString) == 1 and _charIsSep


def _charIsNumberDecimalDigit(aChar):
    return unicodedata.category(aChar) == "Nd"


def _charIsLower(aChar):
    return unicodedata.category(aChar) == "Ll"


def _charIsUpper(aChar):
    return unicodedata.category(aChar) == "Lu"


def _isUpper(aString):
    return len(aString) == 1 and _charIsUpper(aString)


def _isValidAcronym(aString):
    if len(aString) == 0:
        return False

    for aChar in aString:
        if _charIsSep(aChar):
            return False

    return True


def _determine_case(was_upper, words, string):
    """
    Determine case type of string.

    Arguments:
        was_upper {[type]} -- [description]
        words {[type]} -- [description]
        string {[type]} -- [description]

    Returns:
        - upper: All words are upper-case.
        - lower: All words are lower-case.
        - pascal: All words are title-case or upper-case. Note that the
                  stringiable may still have separators.
        - camel: First word is lower-case, the rest are title-case or
                 upper-case. stringiable may still have separators.
        - mixed: Any other mixing of word casing. Never occurs if there are
                 no separators.
        - unknown: stringiable contains no words.

    """
    case_type = "unknown"
    if was_upper:
        case_type = "upper"
    elif string.islower():
        case_type = "lower"
    elif len(words) > 0:
        camel_case = words[0].islower()
        pascal_case = words[0].istitle() or words[0].isupper()

        if camel_case or pascal_case:
            for word in words[1:]:
                c = word.istitle() or word.isupper()
                camel_case &= c
                pascal_case &= c
                if not c:
                    break

        if camel_case:
            case_type = "camel"
        elif pascal_case:
            case_type = "pascal"
        else:
            case_type = "mixed"

    return case_type


def _advanced_acronym_detection(s, i, words, acronyms):
    """
    Detect acronyms by checking against a list of acronyms.

    Check a run of words represented by the range [s, i].
    Return last index of new word groups.
    """
    # Combine each letter into single string.
    acstr = "".join(words[s:i])

    # List of ranges representing found acronyms.
    range_list = []
    # Set of remaining letters.
    not_range = set(range(len(acstr)))

    # Search for each acronym in acstr.
    for acronym in acronyms:
        # TODO: Sanitize acronyms to include only letters.
        rac = re.compile(acronym)

        # Loop until all instances of the acronym are found,
        # instead of just the first.
        n = 0
        while True:
            m = rac.search(acstr, n)
            if not m:
                break

            a, b = m.start(), m.end()
            n = b

            # Make sure found acronym doesn't overlap with others.
            ok = True
            for r in range_list:
                if a < r[1] and b > r[0]:
                    ok = False
                    break

            if ok:
                range_list.append((a, b))
                for j in xrange(a, b):
                    not_range.remove(j)

    # Add remaining letters as ranges.
    for nr in not_range:
        range_list.append((nr, nr + 1))

    # No ranges will overlap, so it's safe to sort by lower bound,
    # which sort() will do by default.
    range_list.sort()

    # Remove original letters in word list.
    for _ in xrange(s, i):
        del words[s]

    # Replace them with new word grouping.
    for j in xrange(len(range_list)):
        r = range_list[j]
        words.insert(s + j, acstr[r[0] : r[1]])

    return s + len(range_list) - 1


def _simple_acronym_detection(s, i, words, *args):
    """Detect acronyms based on runs of upper-case letters."""
    # Combine each letter into a single string.
    acronym = "".join(words[s:i])

    # Remove original letters in word list.
    for _ in xrange(s, i):
        del words[s]

    # Replace them with new word grouping.
    words.insert(s, "".join(acronym))

    return s


class InvalidAcronymError(Exception):
    """Raise when acronym fails validation."""

    def __init__(self, acronym):
        super(InvalidAcronymError, self).__init__()
        m = "Case Conversion: acronym '{}' is invalid."
        print(m.format(acronym))


def _sanitize_acronyms(unsafe_acronyms):
    """
    Check acronyms against regex.

    Normalize valid acronyms to upper-case.
    If an invalid acronym is encountered raise InvalidAcronymError.
    """
    acronyms = []
    for a in unsafe_acronyms:
        if _isValidAcronym(a):
            acronyms.append(a.upper())
        else:
            raise InvalidAcronymError(a)
    return acronyms


def _normalize_words(words, acronyms):
    """Normalize case of each word to PascalCase."""
    for i, _ in enumerate(words):
        # if detect_acronyms:
        if words[i].upper() in acronyms:
            # Convert known acronyms to upper-case.
            words[i] = words[i].upper()
        else:
            # Fallback behavior: Preserve case on upper-case words.
            if not words[i].isupper():
                words[i] = words[i].capitalize()
    return words


def _separate_words(string):
    """
    Segment string on separator into list of words.

    Arguments:
        string -- the string we want to process

    Returns:
        words -- list of words the string got minced to
        separator -- the separator char intersecting words
        was_upper -- whether string happened to be upper-case
    """
    words = []
    separator = ""

    # Index of current character. Initially 1 because we don't want to check
    # if the 0th character is a boundary.
    i = 1
    # Index of first character in a sequence
    s = 0
    # Previous character.
    p = string[0:1]

    # Treat an all-caps stringiable as lower-case, so that every letter isn't
    # counted as a boundary.
    was_upper = False
    if string.isupper():
        string = string.lower()
        was_upper = True

    # Iterate over each character, checking for boundaries, or places where
    # the stringiable should divided.
    while i <= len(string):
        c = string[i : i + 1]

        split = False
        if i < len(string):
            # Detect upper-case letter as boundary.
            if _charIsUpper(c):
                split = True
            # Detect transition from separator to not separator.
            elif not _charIsSep(c) and _charIsSep(p):
                split = True
            # Detect transition not separator to separator.
            elif _charIsSep(c) and not _charIsSep(p):
                split = True
        else:
            # The loop goes one extra iteration so that it can handle the
            # remaining text after the last boundary.
            split = True

        if split:
            if not _charIsSep(p):
                words.append(string[s:i])
            else:
                # stringiable contains at least one separator.
                # Use the first one as the stringiable's primary separator.
                if not separator:
                    separator = string[s : s + 1]

                # Use None to indicate a separator in the word list.
                words.append(None)
                # If separators weren't included in the list, then breaks
                # between upper-case sequences ("AAA_BBB") would be
                # disregarded; the letter-run detector would count them as one
                # sequence ("AAABBB").
            s = i

        i += 1
        p = c

    return words, separator, was_upper


def parse_case(string, acronyms=None, preserve_case=False):
    """
    Parse a stringiable into a list of words.

    Also returns the case type, which can be one of the following:
        - upper: All words are upper-case.
        - lower: All words are lower-case.
        - pascal: All words are title-case or upper-case. Note that the
                  stringiable may still have separators.
        - camel: First word is lower-case, the rest are title-case or
                 upper-case. stringiable may still have separators.
        - mixed: Any other mixing of word casing. Never occurs if there are
                 no separators.
        - unknown: stringiable contains no words.

    Also returns the first separator character, or False if there isn't one.

    """
    words, separator, was_upper = _separate_words(string)

    if acronyms:
        # Use advanced acronym detection with list
        acronyms = _sanitize_acronyms(acronyms)
        check_acronym = _advanced_acronym_detection
    else:
        acronyms = []
        # Fallback to simple acronym detection.
        check_acronym = _simple_acronym_detection

    # Letter-run detector

    # Index of current word.
    i = 0
    # Index of first letter in run.
    s = None

    # Find runs of single upper-case letters.
    while i < len(words):
        word = words[i]
        if word is not None and _isUpper(word):
            if s is None:
                s = i
        elif s is not None:
            i = check_acronym(s, i, words, acronyms) + 1
            s = None

        i += 1

    if s is not None:
        check_acronym(s, i, words, acronyms)

    # Separators are no longer needed, so they can be removed. They *should*
    # be removed, since it's supposed to be a *word* list.
    words = [w for w in words if w is not None]

    # Determine case type.
    case_type = _determine_case(was_upper, words, string)

    if preserve_case:
        if was_upper:
            words = [w.upper() for w in words]
    else:
        words = _normalize_words(words, acronyms)

    return words, case_type, separator
