import re
from bs4 import BeautifulSoup


def chunk(text, chunk_size):
    """
    Chunk a block of text up in N chunks where N is the `chunk_size` passed into
    this function.

    This function will not be exact, because it will not split a single word
    into multiple.
    """
    chunks = []
    words = text.split()

    while words:
        chunks.append(_chunk(words, chunk_size=chunk_size))

    return chunks


def html_to_text(html):
    import html2text

    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.ignore_emphasis = True

    res = converter.handle(html)
    res = re.compile("#+").sub("", res)
    res = re.compile("^\\s+").sub("", res)

    return res


def _chunk(words, chunk_size):
    """
    Helper that takes in a list of words and returns a string of words that
    represents the first "chunk" of `chunk_size`.

    This function continuously modifies the `words` list passed in, popping
    words off of the front of the list to combine together into a string.

        ```
        words = "this is just a silly little test with some random words".split()

        _chunk(words, chunk_size=5) # => 'this is'
        _chunk(words, chunk_size=5) # => 'just a'
        _chunk(words, chunk_size=5) # => 'silly'
        _chunk(words, chunk_size=5) # => 'little'
        _chunk(words, chunk_size=5) # => 'test with'
        _chunk(words, chunk_size=5) # => 'some random'
        _chunk(words, chunk_size=5) # => 'words'
        _chunk(words, chunk_size=5) # => ''
        ```
    """
    chunk = []
    word_count = 0

    while words:
        word = words.pop(0)
        chunk.append(word)
        word_count += len(word)

        if word_count >= chunk_size:
            break

    return " ".join(chunk)
