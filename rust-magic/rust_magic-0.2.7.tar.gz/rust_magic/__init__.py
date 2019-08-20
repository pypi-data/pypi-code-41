from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from subprocess import run, PIPE, STDOUT, Popen
from textwrap import dedent
from time import perf_counter as clock

__version__ = '0.2.7'

@magics_class
class MyMagics(Magics):
    @line_cell_magic
    def rust(self, line, cell=None):
        "Magic that works both as %lcmagic and as %%lcmagic"
        print_wrapper =  dedent('''\
                fn main(){
                    println!("{:?}", (||{
                        %s
                    })());
                }\
        ''')
        run_wrapper =  '''\
                fn main(){
                    %s
                }\
        ''' 
        opts = ''
        if cell is None:
            if line.rstrip().endswith(';'):
                body = run_wrapper % line
            else:
                body = print_wrapper % line
        else:
            opts = line.strip()
            if opts:
                opts = opts.split('#', 1)[0] + ' '
            if 'fn main(' in cell:
                body = cell
            else:
                if cell.rstrip().endswith(';'):
                    body = run_wrapper % cell
                else:
                    body = print_wrapper % cell
        open('cell.rs', 'w').write(body)
        with Popen(('cargo script %scell.rs' % opts).split(), stdout=PIPE, stderr=STDOUT) as proc:
            while True:
                line = proc.stdout.readline()
                if line:
                    print(line.decode().rstrip())
                else:
                    break
    
    @line_cell_magic
    def trust(self, line, cell=None):
        t1 = clock()
        self.rust(line, cell)
        t2 = clock()
        print('Took %.0f ms' % ((t2-t1)*1000))


def load_ipython_extension(ipython):
    ipython.register_magics(MyMagics)
