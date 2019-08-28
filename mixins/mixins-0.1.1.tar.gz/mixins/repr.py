class ReprMixin:
    """
    Sets class __repr__ method based on the attributes named in repr_cols.
    """
    repr_cols = []

    def __repr__(self):
        if self.repr_cols:
            repr_col_strs = [f'{col}={getattr(self, col, None).__repr__()}' for col in self.repr_cols]
            repr_col_str = f'({", ".join(repr_col_strs)})'
        else:
            repr_col_str = ''
        return f'<{type(self).__name__}{repr_col_str}>'

    @property
    def readable_repr(self):
        return show_contents(self)


def show_contents(obj):
    """
    Used to view what's inside an object with pretty printing
    :param obj:
    :return:
    """
    print(_readable_repr(repr(obj)))


def _readable_repr(repr_str):
    out_letters = []
    num_tabs = 1
    for letter in repr_str:
        if letter in (')',']'):
            num_tabs -= 1
            out_letters += ['\n'] + ['   '] * num_tabs
        out_letters.append(letter)
        if letter in ('(','['):
            out_letters += ['\n'] + ['   '] * num_tabs
            num_tabs += 1
    return ''.join(out_letters)