import string
from typing import List
import re


def replace_punctuation(
    sentence: str,
    symbols: List[str] = string.punctuation,
    patterns: List[callable] = [lambda x: f" {x} ", lambda x: f"{x} "],
    replace_by: str = " ",
) -> str:
    """Remove punctuation from a sentence.

    Args:
        - sentence: The sentence to be modified
        - symbols: a list of string representing the symbols
            default is string.punctuation
        - patterns: a list of callables representing lambda functions
            to construct pattern around currently selection punctuation
            symbol
        - replace_by: replacement character

    Requires:
        Condition

    Effects or Returns:
        Value

    """
    for punctuation in string.punctuation:
        for pattern in patterns:
            sentence = sentence.replace(pattern(punctuation), replace_by)
    return sentence


def to_lower(sentence: str) -> str:
    """Transform a sentence to lower."""
    return sentence.lower()


def remove_multiple_spaces(sentence: str) -> str:
    """Remove multiple spaces in sentence."""
    return re.sub(" +", " ", sentence)


def remove_special_characters(
    sentence: str,
    characters: List[str] = ["\t", "\r", "\n"],
    replace_by: str = " ",
) -> str:
    """Remove special characters from a sentence.

    Args:
        - sentence: the sentence to be modified
        - characters: list of characters to be removed
        - replace_by: replacement character

    Returns:
        The modified sentence

    """
    for character in characters:
        sentence = sentence.replace(character, replace_by)
    return sentence


def strip(sentence: str):
    """Strip a sentence."""
    return sentence.strip()


def remove_numbers(sentence: str):
    """Remove numbers from a sentence."""
    parts = []
    for word in sentence.split(" "):
        if not word.isnumeric():
            parts.append(word)
    return " ".join(parts)


def replace_numbers(sentence: str, replace_by: str = "0"):
    """Replace numbers from a sentence."""
    parts = []
    for word in sentence.split(" "):
        if word.isnumeric():
            parts.append(re.sub(r"\d", replace_by, word))
    return " ".join(parts)


def preprocess_sentence(
    sentence: str,
    should_lower: bool = True,
    should_replace_punctuation: bool = True,
    punctuation_symbols: List[str] = string.punctuation,
    punctuation_patterns: List[callable] = [
        lambda x: f" {x} ",
        lambda x: f"{x} ",
    ],
    punctuation_replace_by: str = " ",
    should_replace_special_characters: bool = True,
    special_characters: List[str] = ["\t", "\r", "\n"],
    special_replace_by: str = " ",
    should_replace_numbers: bool = False,
    numbers_replace_by: str = "0",
    should_remove_numbers: bool = False,
):
    if should_lower:
        sentence = to_lower(sentence)

    if should_replace_punctuation:
        sentence = replace_punctuation(
            sentence,
            symbols=punctuation_symbols,
            patterns=punctuation_patterns,
            replace_by=punctuation_replace_by,
        )

    if should_replace_special_characters:
        sentence = remove_special_characters(
            sentence,
            characters=special_characters,
            replace_by=special_replace_by,
        )

    sentence = remove_multiple_spaces(sentence)
    sentence = strip(sentence)

    if should_replace_numbers:
        sentence = replace_numbers(sentence, numbers_replace_by)

    if should_remove_numbers:
        sentence = remove_numbers(sentence)

    return sentence
