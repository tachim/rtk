import cPickle as pickle
import functools
import hashlib
import os
import subprocess
import tempfile
from glob import glob

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

def _get_key(f, version, args, kwargs):
    key_args = [a.tobytes() if isinstance(a, np.ndarray) else a for a in args]
    return hashlib.md5(str((f.__name__, version) + tuple(key_args) + tuple(kwargs.items()))).hexdigest()

_memcache = {}

def memcached():
    def dec(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            k = _get_key(f, None, args, kwargs)
            if k not in _memcache:
                _memcache[k] = f(*args, **kwargs)
            return _memcache[k]
        return wrapper
    return dec


def filecached(dir='/tmp/', version=1):
    def dec(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            k = _get_key(f, version, args, kwargs)
            fname = os.path.join(dir, f.__name__ + ':' + k + '.pickle')
            print fname
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

def make_movie(directory, pattern='frame_%?%?%?%?%?.png', framerate=15, scale='600:400'):
    last_dir = filter(bool, directory.split('/'))[-1]
    movie_path = '%s/%s_out.mp4' % (directory, last_dir)
    print 'Saving movie to %s/%s_out.mp4' % (directory, last_dir)
    cmd = ['ffmpeg', '-framerate', str(framerate), 
            '-i', '%s/%s' % (directory, pattern), 
            '-c:v', 'libx264', '-r', '30', '-crf', '0', '-pix_fmt', 'yuv420p', 
            '-vf', 'scale=%s' % scale,
            movie_path, '-y',
            ]
    run(cmd, capture_stdout=False, print_stdout=True)
    return movie_path

def tmpf(*args, **kwargs):
    return tempfile.mkstemp(*args, **kwargs)[1]
