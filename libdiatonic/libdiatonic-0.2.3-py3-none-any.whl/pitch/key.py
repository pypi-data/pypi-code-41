import string
from .note import Note
from .mode import Mode

__all__ = ('Key',)


class Key(object):
    """ Class representing a musical key

    >>> cmin = Key('C-')
    >>> cmin.relative_major
    Key(Eb)
    >>> cloc = Key('C', mode=Mode.Locrian)
    >>> cloc.relative_minor
    Key(Bb-)
    >>> key = Key('G')
    >>> key.mode.name
    'Major'
    >>> key.root = 'A'
    >>> str(key)
    'A'
    >>> Key('G').to_root('D')
    Key(D)
    """

    def __init__(self, content, mode=None):
        self._content = content
        self.root, remainder = Note.split_str(content)
        if remainder and mode:
            raise ValueError('could not construct key "{}" with mode "{}"'.format(content, mode))
        elif not mode:
            self.mode = None
            for mode in Mode.all():
                if remainder in mode.shorthand:
                    self.mode = mode
            if self.mode is None:
                raise ValueError(
                    'did not recognize mode of key "{}" ({})'.format(content, remainder)
                )
        elif type(mode) != Mode:
            raise TypeError('received valid input for mode: {}'.format(mode))
        else:
            self.mode = mode

        for lookup in (Note.sharps(), Note.flats()):
            self.note_lookup_list = lookup
            self.diatonic_notes = self._find_diatonic_notes_in_lookup(lookup)
            if self.diatonic_notes:
                break
        if not self.diatonic_notes:
            raise ValueError('{} is not a realistic key, try rooting at {}'.format(
                self, self.root.enharmonic_equivalent
            ))

    def _find_diatonic_notes_in_lookup(self, note_lookup_list):
        """ Return a flat list of the notes in the key

        >>> Key('C')._find_diatonic_notes_in_lookup(Note.sharps())
        [Note(C), Note(D), Note(E), Note(F), Note(G), Note(A), Note(B)]
        """
        ret = []
        current_note = self.root
        next_note_i = self.root.chromatic_index
        for half_steps in self.mode.half_steps_pattern:
            ret.append(current_note)
            current_letter_i = string.ascii_uppercase.find(current_note.letter)
            next_note_i = (next_note_i + half_steps) % 12
            for next_note in (note_lookup_list[next_note_i]):
                good_note = False
                next_letter_i = string.ascii_uppercase.find(next_note.letter)
                if next_letter_i - current_letter_i in (1, -6):
                    good_note = True
                    break
            if not good_note:
                return None
            current_note = next_note
        return ret

    def _stitch_content(self):
        ret = str(self.root)
        if self.mode.shorthand:
            ret += self.mode.shorthand[0]
        else:
            ret += ':' + self.mode.name
        return ret

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._stitch_content())

    def __str__(self):
        return self._stitch_content()

    def __eq__(self, other):
        if type(other) == type(self):
            if repr(other) == repr(self):
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_root(self, new_root):
        return Key(new_root, mode=self.mode)

    @property
    def relative_major(self):
        if self.mode.ionian_interval is None:
            raise AttributeError('{} does not have a relative major'.format(self))
        ionian_interval_z = self.mode.ionian_interval - 1
        new_root = self.diatonic_notes[(0 - ionian_interval_z) % 7]
        return Key(new_root)

    @property
    def relative_minor(self):
        if self.mode.ionian_interval is None:
            raise AttributeError('{} does not have a relative minor'.format(self))
        ionian_interval_z = self.mode.ionian_interval - 1
        new_root = self.diatonic_notes[(5 - ionian_interval_z) % 7]
        return Key(new_root, mode=Mode.Aeolian)

    @property
    def transposable_roots(self):
        """ A list of all roots to which this key can reasonably be transposed

        >>> Key('D').transposable_roots  # doctest: +NORMALIZE_WHITESPACE
        [Note(A), Note(Bb), Note(B), Note(Cb), Note(C), Note(C#), Note(Db),
         Note(Eb), Note(E), Note(F), Note(F#), Note(Gb), Note(G), Note(Ab)]
        """
        ret = []
        for chromatic_index in range(12):
            for note in Note.all()[chromatic_index]:
                if note == self.root:
                    continue
                try:
                    self.to_root(note)
                    ret.append(note)
                except ValueError:
                    pass
        return ret
