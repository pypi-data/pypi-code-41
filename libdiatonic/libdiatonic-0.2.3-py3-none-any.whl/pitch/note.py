import collections
import re

__all__ = ('Note',)

NOTE_STR_REGEX = re.compile(r'^[A-Ga-g][b#]?$')


class Note(object):
    """ Class representing a musical note

    >>> note = Note('A')
    >>> note
    Note(A)
    >>> str(note)
    'A'
    """

    _chromatic_index_map = collections.OrderedDict([
        ('A', 0), ('A#', 1), ('Bb', 1), ('B', 2), ('Cb', 2), ('B#', 3), ('C', 3),
        ('C#', 4), ('Db', 4), ('D', 5), ('D#', 6), ('Eb', 6), ('E', 7), ('Fb', 7),
        ('E#', 8), ('F', 8), ('F#', 9), ('Gb', 9), ('G', 10), ('G#', 11), ('Ab', 11)
    ])

    def __init__(self, content):
        if isinstance(content, self.__class__):
            content = content._content
        else:
            if NOTE_STR_REGEX.match(content) is None:
                raise ValueError('"{0}" is not a valid input for a Note'.format(content))
            content = content.capitalize()
        self._content = content

    def __str__(self):
        return self._content

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._content)

    def __eq__(self, other):
        if type(other) == type(self):
            if repr(other) == repr(self):
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def split_str(cls, content):
        """ Split a string into a Note object and a string containing the remainder

        >>> Note.split_str('C#asdf')
        (Note(C#), 'asdf')
        """
        if content.__class__ == cls:
            content = str(content)
        if len(content) == 1:
            return cls(content), ''
        try:
            ret = cls(content[:2])
            remainder = content[2:]
        except ValueError:
            ret = Note(content[:1])
            remainder = content[1:]
        return ret, remainder

    @classmethod
    def all(cls, flatten=False):
        """ Return a chromatic scale including all standard notes, starting with A

        >>> Note.all()  # doctest: +NORMALIZE_WHITESPACE
        [[Note(A)], [Note(A#), Note(Bb)], [Note(B), Note(Cb)], [Note(B#), Note(C)],
         [Note(C#), Note(Db)], [Note(D)], [Note(D#), Note(Eb)], [Note(E), Note(Fb)],
         [Note(E#), Note(F)], [Note(F#), Note(Gb)], [Note(G)], [Note(G#), Note(Ab)]]
        """
        ret = []
        for note, index in cls._chromatic_index_map.items():
            if len(ret) == index:
                ret.append([cls(note)])
            else:
                ret[-1].append(cls(note))
        return ret

    @classmethod
    def sharps(cls):
        """ Return a chromatic scale of sharps, starting with A

        >>> Note.sharps()  # doctest: +NORMALIZE_WHITESPACE
        [[Note(A)], [Note(A#)], [Note(B)], [Note(B#), Note(C)], [Note(C#)], [Note(D)],
         [Note(D#)], [Note(E)], [Note(E#), Note(F)], [Note(F#)], [Note(G)], [Note(G#)]]
        """
        ret = []
        for note, index in cls._chromatic_index_map.items():
            if 'b' not in note:
                if len(ret) == index:
                    ret.append([cls(note)])
                else:
                    ret[-1].append(cls(note))
        return ret

    @classmethod
    def flats(cls):
        """ Return a chromatic scale of flats, starting with A

        >>> Note.flats()  # doctest: +NORMALIZE_WHITESPACE
        [[Note(A)], [Note(Bb)], [Note(B), Note(Cb)], [Note(C)], [Note(Db)], [Note(D)],
         [Note(Eb)], [Note(E), Note(Fb)], [Note(F)], [Note(Gb)], [Note(G)], [Note(Ab)]]
        """
        ret = []
        for note, index in cls._chromatic_index_map.items():
            if '#' not in note:
                if len(ret) == index:
                    ret.append([cls(note)])
                else:
                    ret[-1].append(cls(note))
        return ret

    @property
    def lookup_list(self):
        """ Each Note "prefers" sharps or flats when determining its relationship to other notes

        >>> Note('F').lookup_list  # doctest: +NORMALIZE_WHITESPACE
        [[Note(A)], [Note(Bb)], [Note(B), Note(Cb)], [Note(C)], [Note(Db)], [Note(D)],
         [Note(Eb)], [Note(E), Note(Fb)], [Note(F)], [Note(Gb)], [Note(G)], [Note(Ab)]]
        """
        if 'b' in self._content or self._content == 'F':
            return self.flats()
        return self.sharps()

    @property
    def chromatic_index(self):
        """ Essentially a numeric value for a given Note

        This value can be shared by multiple Notes

        >>> Note('C').chromatic_index
        3
        """
        return self._chromatic_index_map[self._content]

    @property
    def enharmonic_equivalent(self):
        """ Return the *other* Note with the same chromatic_index as the current Note

        If the current Note does not share its chromatic_index with another Note, a
        ValueError is raised.

        >>> Note('Eb').enharmonic_equivalent
        Note(D#)
        """
        notes = [k for k, v in self._chromatic_index_map.items() if v == self.chromatic_index]
        if len(notes) == 1:
            raise ValueError('{} has no enharmonic equivalent'.format(repr(self)))
        return Note(notes[1]) if notes[0] == self else Note(notes[0])

    @property
    def letter(self):
        """ Return the letter component of the Note name

        >>> Note('C').letter
        'C'
        >>> Note('Bb').letter
        'B'
        """
        return self._content[0]

    def is_sharp(self):
        return '#' in str(self)

    def is_flat(self):
        return 'b' in str(self)
