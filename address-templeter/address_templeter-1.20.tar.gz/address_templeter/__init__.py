#!/usr/bin/python
# -*- coding: utf-8 -*-

import pycrfsuite
import os
import re
import warnings
from collections import OrderedDict

#  _____________________
# |1. LABELS! |
# |_____________________|
#     (\__/) ||
#     (•ㅅ•) ||
#     / 　 づ

OTHER_LABELS = ["OtherNumber",  # 312311
                "OtherText",  # открыто с
                "PunctuationMark",  # , ()
                "Comma"
                ]

INDEX = ["PostCode",  # 04122
         "PostCode_"  # moving PostCode
         ]

PLACE = ["PlacePretext",  # г.
                 ]
REGION = [
    "RegionPretext",  # Область
]
STREET = [
    "StreetPretext"  # ул, бульвар
]
HOUSE_NAME = ["HouseName",  # дом культуры
              "HousePretext",  # буд
              ]
HOUSE_NUMBER = ["HouseNumber"  # 55
                ]
LABELS = ["Place",  # Киев
          "Region",  # Киевская
          "Street",  # Амосова
          "Dash",  # -
          ]  # The labels should be a list of strings

LABELS = LABELS + OTHER_LABELS + PLACE + REGION + STREET + HOUSE_NAME + INDEX + HOUSE_NUMBER

STREET_PRETEXT = {"вул": "вулиця", "вулиця": "вулиця", "ул": "улица", "улица": "улица",
                  "проспект": "проспект", "просп": "проспект", "шоссе": "шоссе", "шосе": "шоссе", "пл": "площадь",
                  "площа": "площа", "бульвар": "бульвар", "бул": "бульвар", "пров": "провулок", "автошлях": "автошлях",
                  "узвіз": "узвіз", "пр-т": "проспект", "б-р": "бульвар", "провулок": "провулок", "бульв": "бульвар",
                  "пер": "переулок"}

PLACE_PRETEXT = ["м", "город", "місто", "село",
                 "смт", "пгт", "г", "п"]

REGION_PRETEXT = {"р-н": "район", "район": "район", "обл": "область", "область": "область",
                  "регион": "регион", "регіон": "регіон", "района": "район", "области": "область"}

HOUSE_PRETEXT = ["буд", "будинок", "д", "дом", "магазин",
                 "трц", "ринок", "ст", "отель", 'районний',
                 "ресторан", "кофе", "pab", 'виховний',
                 'комплекс', 'ринок', 'центр', 'маркет',
                 'футбольна', 'школа', 'поліклініка', 'району',
                 'районна', 'адміністрація', 'обслуговування', 'церква',
                 'академія', 'управління', 'податкова', 'офис',
                 'метро', 'титул', 'національний', 'університет',
                 'театр', 'кіно', 'телебачення', 'склад', 'корпус', 'садок',
                 'поликлиника', 'інтернат', 'будинок', 'поліція',
                 'лікарня', 'станція', 'клуб', 'ліцей', "площа", "б", 'антикафе']

PUNCTUATION_MARK = ["(", ")", "!", "?", "#", ":"]

COMMA = [","]

DASH = ["-"]

# ***************** OPTIONAL CONFIG ***************************************************
MODEL_FILE = 'learned_settings.crfsuite'  # filename for the crfsuite settings file
# ************************************************************************************


try:
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(os.path.split(os.path.abspath(__file__))[0] + '/' + MODEL_FILE)
except IOError:
    TAGGER = None
    warnings.warn(
        'You must train the model (parserator train [traindata] [modulename]) to create the %s file before you can use the parse and tag methods' % MODEL_FILE)


def parse(raw_string: str) -> list:
    if not TAGGER:
        raise IOError(
            '\nMISSING MODEL FILE: %s\n'
            'You must train the model before you can use the parse and tag methods\n'
            'To train the model annd create the model file, run:\n'
            'parserator train [traindata] [modulename]' % MODEL_FILE)

    tokens = tokenize(raw_string)
    if not tokens:
        return []

    features = tokens2features(tokens)

    tags = TAGGER.tag(features)
    return list(zip(tokens, tags))


def tag(raw_string):
    tagged = OrderedDict()
    for token, label in parse(raw_string):
        tagged.setdefault(label, []).append(token)

    for token in tagged:
        component = ' '.join(tagged[token])
        component = component.strip(' ,;')
        tagged[token] = component

    return tagged


#  _____________________
# |2. TOKENS! |
# |_____________________|
#     (\__/) ||
#     (•ㅅ•) ||
#     / 　 づ
def tokenize(raw_string):
    # this determines how any given string is split into its tokens
    # handle any punctuation you want to split on, as well as any punctuation to capture

    if isinstance(raw_string, bytes):
        try:
            raw_string = str(raw_string, encoding='utf-8')
        except:
            raw_string = str(raw_string)

    re_tokens = re.compile(r"[\,\(\)\&\?\#\!\:]|[^\s\.\)\(\,]+")
    tokens = re_tokens.findall(raw_string)

    if not tokens:
        return []
    return tokens


#  _______________________
# |3. FEATURES! |
# |_______________________|
#     (\__/) ||
#     (•ㅅ•) ||
#     / 　 づ
def tokens2features(tokens):
    # this should call tokenFeatures to get features for individual tokens,
    # as well as define any features that are dependent upon tokens before/after

    feature_sequence = [tokenFeatures(tokens[0])]
    previous_features = feature_sequence[-1].copy()

    for token in tokens[1:]:
        # set features for individual tokens (calling tokenFeatures)
        token_features = tokenFeatures(token)
        current_features = token_features.copy()

        # features for the features of adjacent tokens
        feature_sequence[-1]['next'] = current_features
        token_features['previous'] = previous_features

        # DEFINE ANY OTHER FEATURES THAT ARE DEPENDENT UPON TOKENS BEFORE/AFTER
        # for example, a feature for whether a certain character has appeared previously in the token sequence

        feature_sequence.append(token_features)
        previous_features = current_features

    if len(feature_sequence) > 1:
        # these are features for the tokens at the beginning and end of a string
        feature_sequence[0]['rawstring.start'] = True
        feature_sequence[-1]['rawstring.end'] = True
        feature_sequence[1]['previous']['rawstring.start'] = True
        feature_sequence[-2]['next']['rawstring.end'] = True

    else:
        # a singleton feature, for if there is only one token in a string
        feature_sequence[0]['singleton'] = True

    return feature_sequence


def tokenFeatures(token):
    # this defines a dict of features for an individual token
    features = {
        'length': len(token),
        'case': casing(token),
        'in_pretext': in_pre(token),
        'digit_in': digits(token),
        'begin_with_sign': (token[0]
                            if bool(re.match('^[^.\w]', token, flags=re.UNICODE))
                            else False),
        'ends_with_sign': (token[-1]
                           if bool(re.match('.+[^.\w]', token, flags=re.UNICODE))
                           else False),
        'with_dash': dash_id(token)
    }

    return features


def dash_id(token):
    if token.find('-') == -1:
        return 'none dash'
    elif re.fullmatch(r'\D+-\D+', token):
        return 'word-word'
    elif re.fullmatch(r'\d+-\D+', token):
        return 'digit-word'
    elif re.fullmatch(r'\D+-\d+', token):
        return 'word-digit'
    elif re.fullmatch(r'\d+-\d+', token):
        return 'digit-digit'
    else:
        return 'other'


def casing(token):
    """
    capitalization check in token
    :param token
    :return: str type
    """
    if token.isupper():
        return 'upper'
    elif token.islower():
        return 'lower'
    elif token.istitle():
        return 'title'
    elif token.isalpha():
        return 'mixed'
    else:
        return False


def in_pre(token):
    """
    LABELS affiliation
    :param token:
    :return: LABELS name
    """
    token = token.lower()
    if token in STREET_PRETEXT:
        return "StreetPretext"
    elif token in PLACE_PRETEXT:
        return "PlacePretext"
    elif token in REGION_PRETEXT:
        return "RegionPretext"
    elif token in HOUSE_PRETEXT:
        return "HousePretext"
    elif token in PUNCTUATION_MARK:
        return "PunctuationMark"
    elif token in COMMA:
        return "Comma"
    elif token in DASH:
        return "Dash"
    else:
        return "Other"


def digits(token: str) -> str:
    """
    The presence of numbers on different sides of the token
    :param token:
    :return:
    """
    if token.isdigit():
        if int(token) == 0:
            return "zero"
        return "isdigit"
    elif token[0].isdigit() and token[-1].isdigit():
        return 'begin_and_end'
    elif token[0].isdigit():
        return "in_begin"
    elif token[-1].isdigit():
        return "in_end"
    elif bool(re.findall(r"\d", token)):
        return "digit_within"
    else:
        return "no_digit"


def clean(address: str, place_pretext: bool = False, region_pretext: bool = False,
          address_pretext: bool = False, house: bool = False, index: bool = False) -> str:
    """removes whitespace characters, pinching tricks and unnecessary tokens"""

    def concat_address_number(address_array):
        for index, word in enumerate(address_array.copy()):
            if index < len(address_array) - 1 and word[1] == address_array[index + 1][1] and word[1] == 'HouseNumber':
                w1 = address_array.pop(index + 1)
                w2 = address_array.pop(index)
                address_array.insert(index, (w2[0] + w1[0], w1[1]))
                address_array = concat_address_number(address_array)
                break
            elif index != 0 and word[1] == 'PostCode':
                i = address_array.pop(index)
                address_array.insert(0, (i[0], 'PostCode_'))
                address_array = concat_address_number(address_array)
                break
        return address_array

    def get_unnecessary_label():
        label_ = OTHER_LABELS if place_pretext else OTHER_LABELS + PLACE
        label_ = label_ if region_pretext else label_ + REGION
        label_ = label_ if address_pretext else label_ + STREET
        label_ = label_ if index else label_ + INDEX

        if house:
            label_ = label_ + HOUSE_NAME if any(p for p in parsed if p[1] == 'HouseNumber') \
                else label_ + HOUSE_NUMBER
        return label_

    address = re.sub(r'\s?\-\s?', '-', address)
    address = re.sub(r'\s?[\\/]\s?', '/', address)
    parsed = parse(address)
    parsed = concat_address_number(parsed)
    non_label = get_unnecessary_label()
    if address_pretext:
        parsed = [(STREET_PRETEXT.get(s[0], s[0]), s[1]) if s[1] == 'StreetPretext' else s for s in parsed]
    if region_pretext:
        parsed = [(REGION_PRETEXT.get(s[0], s[0]), s[1]) if s[1] == 'RegionPretext' else s for s in parsed]
    address_string = " ".join([p[0] for p in parsed if p[1] not in non_label])
    return address_string


if __name__ == '__main__':
    print(clean('Донецк, Ленинский р-н, ул. Куйбышева 6а', address_pretext=True, region_pretext=True))
