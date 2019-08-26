from .interval import Interval
from .note import Note

__all__ = ('ChordSpecToken', 'ChordSpec', 'Chord')


class ChordSpecToken(object):

    valid_token_types = ('modifier', 'interval')

    def __init__(self, token_type, long_str, short_str=None, char=None, symbol=None):
        if token_type not in self.valid_token_types:
            raise ValueError('token_type must be one of ' + self.valid_token_types)
        self.token_type = token_type
        self.long_str = long_str
        self.short_str = short_str
        self.char = char
        self.symbol = symbol

    def __repr__(self):
        return self.long_str.upper()

    @property
    def strings(self):
        return [s for s in (self.long_str, self.short_str, self.char, self.symbol) if s]

    @classmethod
    def from_repr(cls, repr_str):
        return getattr(ChordSpec, 'TOKEN_' + repr_str)


class ChordSpec(object):
    """ Object representing the disposition of a particular chord

    >>> cs = ChordSpec('-7b5')
    >>> cs
    ChordSpec(-7b5)
    >>> str(cs)
    '-7b5'
    """

    TOKEN_MAJOR = ChordSpecToken('modifier', long_str='major', short_str='maj', char='M')
    TOKEN_MINOR = ChordSpecToken('modifier', long_str='minor', short_str='min', char='m',
                                 symbol='-')
    TOKEN_AUGMENTED = ChordSpecToken('modifier', long_str='augmented', short_str='aug',
                                     symbol='+')
    TOKEN_DIMINISHED = ChordSpecToken('modifier', long_str='diminished', short_str='dim',
                                      symbol='°')
    TOKEN_DOMINANT = ChordSpecToken('modifier', long_str='dominant')
    TOKEN_PERFECT = ChordSpecToken('modifier', long_str='perfect')
    TOKEN_SHARP = ChordSpecToken('modifier', long_str='sharp', symbol='#')
    TOKEN_FLAT = ChordSpecToken('modifier', long_str='flat', symbol='b')
    TOKEN_ADD = ChordSpecToken('modifier', long_str='added', short_str='add')
    TOKEN_SUS = ChordSpecToken('modifier', long_str='suspended', short_str='sus')
    TOKEN_TWO = ChordSpecToken('interval', long_str='2')
    TOKEN_THREE = ChordSpecToken('interval', long_str='3')
    TOKEN_FOUR = ChordSpecToken('interval', long_str='4')
    TOKEN_FIVE = ChordSpecToken('interval', long_str='5')
    TOKEN_SIX = ChordSpecToken('interval', long_str='6')
    TOKEN_SEVEN = ChordSpecToken('interval', long_str='7')
    TOKEN_NINE = ChordSpecToken('interval', long_str='9')
    TOKEN_ELEVEN = ChordSpecToken('interval', long_str='11')
    TOKEN_THIRTEEN = ChordSpecToken('interval', long_str='13')

    @classmethod
    def valid_tokens(cls):
        """ Return all tokens defined above as a list """
        attrs = cls.__dict__
        return [attrs[k] for k in attrs.keys() if k.startswith('TOKEN_')]

    @classmethod
    def _sorted_token_string_tuples(cls):
        """ Get a list of all search strings, and the tokens they represent, sorted longest
        to shortest by length.  This is required when tokenizing because some token strings
        are substrings of others.  The exact order of the tuples is not deterministic, but
        the rough order by length is expected to be sufficient.
        """
        ret = []
        for token in cls.valid_tokens():
            for token_str in token.strings:
                if not ret:
                    ret.append((token_str, token))
                    continue
                inserted = False
                for i in range(len(ret)):
                    if len(token_str) > len(ret[i][0]):
                        ret.insert(i, (token_str, token))
                        inserted = True
                        break
                if not inserted:
                    ret.append((token_str, token))
        return ret

    @classmethod
    def tokenize_content(cls, content):
        """ Take tokenizable ChordSpec content and return the tokens """

        # split into individual tokens
        tokens = []
        cursor = 0
        while cursor < len(content):
            subspec = content[cursor:]
            found = False
            for token_str, token in cls._sorted_token_string_tuples():
                if subspec.startswith(token_str):
                    tokens.append(token)
                    cursor += len(token_str)
                    found = True
                    break
            if not found:
                # we've hit a single character that is not a special and not a digit...?
                raise ValueError(
                    'found garbage character "{}" at position {}'.format(subspec[0], cursor)
                )

        if len(tokens) == 0:
            tokens.append(cls.TOKEN_MAJOR)

        return tokens

    @classmethod
    def group_tokens(cls, tokens):
        """ Take a list of ChordSpecTokens and group them into related pairs """

        for token in tokens:
            if token not in cls.valid_tokens():
                raise ValueError('{} is not a valid ChordSpec token')

        groups = []
        cursor = 0
        while cursor < len(tokens):
            advance = 1
            if tokens[cursor].token_type == 'interval':
                groups.append([cls.TOKEN_DOMINANT, tokens[cursor]])
            elif cursor != len(tokens) - 1 and tokens[cursor + 1].token_type == 'interval':
                groups.append(tokens[cursor:cursor + 2])
                advance += 1
            else:
                groups.append([tokens[cursor]])
            cursor += advance
        return groups

    def __init__(self, content):
        self._content = content
        self.tokens = self.tokenize_content(content)
        self.token_groups = self.group_tokens(self.tokens)

    def __str__(self):
        return self._content

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._content)

    def __eq__(self, other):
        if type(self) == type(other) and self.token_groups == other.token_groups:
            return True
        return False

    def __ne__(self, other):
        return not self == other


class Chord(object):
    """ Class representing a musical chord

    >>> Chord('G')
    Chord(G)
    >>> Chord('C#-7')
    Chord(C#-7)
    >>> str(Chord('Ab-7/Gb'))
    'Ab-7/Gb'
    """

    def __init__(self, content):

        self._content = content
        self.spec = self.base = ''
        self.root, remainder = Note.split_str(content)
        if not remainder:
            return

        tokens = remainder.split('/')
        if len(tokens) > 2:
            raise ValueError(
                'could not parse "{}" as a chord: too many "/"s'.format(content)
            )
        elif len(tokens) == 2:
            if not tokens[1]:
                raise ValueError('could not parse "{}" as a chord: empty base'.format(content))
            self.base = Note(tokens[1])
        self.spec = ChordSpec(tokens[0])

    def _stitch_content(self):
        ret = str(self.root) + str(self.spec)
        if self.base:
            ret = '/'.join((ret, str(self.base)))
        return ret

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._stitch_content())

    def __str__(self):
        return self._stitch_content()

    def __ne__(self, other):
        if type(self) != type(other):
            return True
        for attr in ('root', 'spec', 'base'):
            if getattr(self, attr) != getattr(other, attr):
                return True
        return False

    def __eq__(self, other):
        return not self != other

    @classmethod
    def from_parts(cls, root, spec: ChordSpec = None, base: Note = None) -> 'Chord':
        content = str(root)
        if spec:
            content += str(spec)
        if base:
            content += f'/{str(base)}'
        return cls(content)

    def transpose_by_half_steps(self, half_steps: int, prefer_sharps: bool = False) -> 'Chord':
        note_lookup_list = Note.sharps() if prefer_sharps else Note.flats()
        from_i = self.root.chromatic_index
        to_i = (from_i + half_steps) % 12
        new_root = note_lookup_list[to_i][0]
        if self.base:
            from_i = self.base.chromatic_index
            to_i = (from_i + half_steps) % 12
            new_base = note_lookup_list[to_i][0]
        else:
            new_base = None
        return self.__class__.from_parts(new_root, self.spec, new_base)

    def transpose_by_new_root(self, new_root: Note, prefer_sharps: bool = False) -> 'Chord':
        interval = Interval.from_notes(self.root, new_root)
        half_steps = interval.half_steps
        # always prefer the directive that comes from the new root (so that it is preserved in the half_steps logic)
        if new_root.is_sharp():
            prefer_sharps = True
        elif new_root.is_flat():
            prefer_sharps = False
        return self.transpose_by_half_steps(half_steps, prefer_sharps)
