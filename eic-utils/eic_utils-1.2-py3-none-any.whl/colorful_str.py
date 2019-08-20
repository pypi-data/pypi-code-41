__all__ = ['colorful_str']
class ColorfulStr(object):# {{{
    """ to make string colorful """
    def __init__(self):
        self.colors = {
            'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
            'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
            'b': 34, 'r': 31, 'g': 32, 'y': 33, 'w': 37,
        }
        self.done = '(#g)done(#)'
        self.prefix = '\033[1;{}m'
        self.suffix = '\033[1;0m'

    def __call__(self, *args, auto_end=True):
        """ return colorful string
            
            (#r) for red, (#b) for blue, (#) for default, etc.
        """
        s = (self.suffix+' ').join(map('{}'.format, args))
        for color, value in self.colors.items():
            color_tag = '(#{})'.format(color)
            s = s.replace(color_tag, self.prefix.format(value))
        s += self.suffix
        s = s.replace('(#)', self.suffix)
        return s

    def err(self, *args):
        return self('(#r)[ERR](#)', *args)

    def log(self, *args):
        return self('(#b)[LOG](#)', *args)

    def wrn(self, *args):
        return self('(#y)[WRN](#)', *args)

    def suc(self, *args):
        return self('(#g)[SUC](#)', *args)

    def dict(self, data):
        assert isinstance(data, dict), 'data must be a dict'
        return self(', '.join(['(#b){}(#): (#y){}(#)'.format(k, v) for k, v in data.items()]))
# }}}
colorful_str = ColorfulStr()

if __name__ == '__main__':
    print(colorful_str('(#r)hi(#)(#b)qweq'))
    print(colorful_str('hi(#)(#b)qweq'))
    print(colorful_str.dict({'a': 's', 'b': 's'}))
