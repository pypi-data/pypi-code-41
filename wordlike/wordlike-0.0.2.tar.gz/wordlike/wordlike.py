#!/usr/bin/env python3.7
"""
Generate wordlike strings based on patterns of strings found in a list of input string.

If you can find a practical application for this module, please let me know!
"""
from random import choice, randint
import pathlib

def init_word_list(dictionary_path):
    """
    Open file from dictionary_path and read.
    Return a list of strings terminating with '\\n'.
    """
    dictionary = pathlib.Path(dictionary_path)
    try:
        word_list = dictionary.read_text()
        return [word+"\n" for word in word_list.split("\n")]
    except FileNotFoundError:
        raise FileNotFoundError(f"Dictionary file doesn't exist: {dictionary_path}")


def get_word(word_list, lookahead=1, start=None):
    """Return a generated wordlike string.
    
    Arguments:
    word_list -- list of '\\n' terminated strings
    lookahead -- index used to match subsequent characters in the string
    start     -- string of characters to start generation
    """    
    if start:
        lookahead = len(start)
    else:
        start = start or choice(word_list)[:lookahead]
    generated_word = start[0]
    while "\n" not in generated_word:
        next = choice([word for word in word_list if start in word])
        shift = next.index(start) + 1
        chunk = next[shift:shift+lookahead]
        generated_word += chunk[0]
        start =  chunk
    return generated_word.strip()

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary", "-d", default="/usr/share/dict/words")
    parser.add_argument("--number", "-n", default=1);
    parser.add_argument("--lookahead", "-l", default=1);
    parser.add_argument("--start", "-t", default=None);
    parser.add_argument("--separator", "-s", default="\n");
    args = parser.parse_args()
    word_list = init_word_list(args.dictionary)
    print(args.separator.join([get_word(word_list, int(args.lookahead), args.start) for _ in range(0,int(args.number))]))
