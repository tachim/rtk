import cPickle as pickle
import functools
import hashlib
import os
import subprocess
import tempfile

class RetCode(Exception): pass

def run(cmd, capture_stdout=True, ignore_ret=False, print_stdout=False):
    if capture_stdout:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ret = []
        for line in iter(process.stdout.readline, ''):
            ret.append(line.strip())
            if print_stdout:
                print line.strip()
        retval = process.wait()
        if retval != 0 and not ignore_ret: raise RetCode()
        return '\n'.join(ret)
    else:
        retval = subprocess.Popen(cmd).wait()
        if retval != 0 and not ignore_ret: raise RetCode()

def ls(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def filecached(dir='/tmp/', version=1):
    def dec(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            k = hashlib.md5(str((f.__name__, version) + tuple(args) + tuple(kwargs.items()))).hexdigest()
            fname = os.path.join(dir, f.__name__ + ':' + k + '.pickle')
            if not os.path.exists(fname):
                ret = f(*args, **kwargs)
                with open(fname, 'wb') as fptr:
                    pickle.dump(ret, fptr, pickle.HIGHEST_PROTOCOL)
            with open(fname, 'rb') as fptr:
                return pickle.load(fptr)
        return wrapper
    return dec

tmpf = tempfile.mkstemp
