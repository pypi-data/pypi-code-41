"""Various functions to clean up a log of Whatsapp messages."""
from collections import Counter

SPECIAL_CHARACTERS = './!?"\n():;'
UNINTERESTING_MESSAGES = [
    '<media omitted>\n',
    'missed voice call\n',
    '\n',
    ''
]
PHRASE_REPLACEMENTS = [
    ('<Media omitted>', '<Media-omitted>'),
    ('missed voice call', 'missed-voice-call')
]


def load_chat_from_path(path):
    """Load Whatsapp chat log from path, with one message per list element."""
    with open(path) as f:
        chat = f.readlines()
    return chat


def clean(messages, character_level=True):
    """Clean Whatsapp chat messages."""
    if character_level:
        return _clean_for_characters(messages)
    return _clean_for_words(messages)


def _clean_for_words(messages):
    """
    Clean Whatsapp chat messages, to the word-level.

    Parameters
    ----------
    messages : list of str
        List of messages used in a Whatsapp chat.

    Returns
    -------
    list of str
        List of words used in a Whatsapp chat in consecutive order, after
        various cleaning steps.
    """
    chat = ' '.join([_remove_timestamp(message) for message in messages])

    chat = _separate_special_character_words(chat)
    chat = _replace_phrases(chat)

    words = chat.lower().split(' ')

    return _filter_low_frequency_tokens(words)


def _clean_for_characters(messages):
    """
    Clean Whatsapp chat messages, to the character-level.

    Parameters
    ----------
    messages : list of str
        List of messages used in a Whatsapp chat.

    Returns
    -------
    list of str
        List of characters used in a Whatsapp chat in consecutive order, after
        various cleaning steps.
    """
    messages = [_remove_timestamp(message) for message in messages]
    messages = [
        message for message in messages if _is_message_interesting(message[14:])]

    chat = ''.join([character for message in messages for character in message])
    return _filter_low_frequency_tokens(chat)


def _remove_timestamp(message):
    """Remove the timestamp from a single message."""
    return message[20:]


def _is_message_interesting(message):
    """Determine whether message is an interesting phrase."""
    return message not in UNINTERESTING_MESSAGES


def _replace_phrases(chat, replacements=PHRASE_REPLACEMENTS):
    for phrase, replacement in replacements:
        chat = chat.replace(phrase, replacement)
    return chat


def _separate_special_character_words(chat, characters=SPECIAL_CHARACTERS):
    for c in characters:
        chat = chat.replace(c, ' {} '.format(c))
    return chat


def _filter_low_frequency_tokens(tokens, minimum_frequency=5):
    """Return tokens in same order, with less frequently used tokens removed."""
    token_counter = Counter(tokens)

    high_frequency_tokens = set()
    for token, count in token_counter.items():
        if count >= minimum_frequency:
            high_frequency_tokens.add(token)

    print('Number of high-frequency tokens'.format(len(high_frequency_tokens)))

    return [token for token in tokens if token in high_frequency_tokens]
