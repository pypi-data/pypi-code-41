import time, datetime
from eic_utils.colorful_str import *

class procedure(object):# {{{
    def __init__(self, msg, same_line=True):
        self.logs, self.same_line = [msg], same_line
        self.time = time.time()

    def __enter__(self):
        print(colorful_str.log(*self.logs), end='\r' if self.same_line else '\n')
        return self

    def add_log(self, *args):
        self.logs += args

    def __exit__(self, type, value, traceback):
        log = colorful_str.suc if traceback is None else colorful_str.err
        print(log(*self.logs, colorful_str.done, 
            'time: (#b){}'.format(datetime.timedelta(seconds=time.time()-self.time))))
# }}}

if __name__ == '__main__':
    with procedure('hi') as p:
        p.add_log('(#r)as')
