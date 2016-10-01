import cPickle as pickle
import functools
import hashlib
import os
import subprocess
import tempfile

import numpy as np

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
            key_args = [a.tobytes() if isinstance(a, np.ndarray) else a for a in args]
            k = hashlib.md5(str((f.__name__, version) + tuple(key_args) + tuple(kwargs.items()))).hexdigest()
            fname = os.path.join(dir, f.__name__ + ':' + k + '.pickle')
            if not os.path.exists(fname):
                ret = f(*args, **kwargs)
                with open(fname, 'wb') as fptr:
                    pickle.dump(ret, fptr, pickle.HIGHEST_PROTOCOL)
            with open(fname, 'rb') as fptr:
                return pickle.load(fptr)
        return wrapper
    return dec

def makedirs(directory):
    try:
        os.makedirs(directory)
    except Exception, e:
        if 'File exists' not in str(e):
            raise

def make_movie(directory, pattern='frame_%?%?%?%?%?.png', framerate=15):
    last_dir = os.path.split(directory)[-1]
    cmd = ['ffmpeg', '-framerate', str(framerate), 
            '-i', '%s/%s' % (directory, pattern), 
            '-c:v', 'libx264', '-r', '30', '-crf', '0', '-pix_fmt', 'yuv420p', 
            '%s/%s_out.mp4' % (last_dir, directory), '-y',
            ]
    run(cmd, capture_stdout=False, print_stdout=True)

def tmpf(*args, **kwargs):
    return tempfile.mkstemp(*args, **kwargs)[1]
