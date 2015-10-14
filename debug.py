""" 

Usage:

    1. import rtk
    2. replace main() with rtk.pdb.wrap(main)()

"""

import os
import pdb
import sys
import traceback

def wrap(f):
    '''A utility for dropping out to a debugger on exceptions.'''
    def fdebug(*a, **kw):
        try:
            return f(*a, **kw)
        except Exception:
            print
            type, value, tb = sys.exc_info()
            traceback.print_exc(file=sys.stderr)
            os.system('stty sane')

            if sys.stdin.isatty():
                pdb.post_mortem(tb)
            else:
                sys.exit(1)
    return fdebug
