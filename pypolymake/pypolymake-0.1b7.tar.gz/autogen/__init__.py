from __future__ import absolute_import

import glob
from os.path import join, exists, getmtime

from .pm_types import pm_modules

from .handlers import (write_handlers,
        write_mappings,
        write_declarations,
        write_definitions,
#        write_undefined_classes
        )

def rebuild(force=False):
    module_path = 'polymake'
    print("*** Rebuilding handlers and mappings ***")

    src_files = glob.glob(join('autogen', '*.py'))
    gen_files = [join(module_path, "auto_handlers.pxi"),
                 join(module_path, "auto_mappings.pxi")] + \
                [join(module_path, '{}.pxd'.format(mod)) for mod in pm_modules()]

    if not force and all(exists(f) for f in gen_files):
        src_mtime = max(getmtime(f) for f in src_files)
        gen_mtime = max(getmtime(f) for f in gen_files)

        if gen_mtime > src_mtime:
            return

    write_handlers(join(module_path, "auto_handlers.pxi"))
    write_mappings(join(module_path, "auto_mappings.pxi"))
    write_declarations()
#    write_undefined_classes()
