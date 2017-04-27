import cPickle as pickle
import functools
import hashlib
import contextlib
import os
import subprocess
import tempfile
from glob import glob

import numpy as np

class RetCode(Exception): pass

def run_bg(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    yield process
    for line in iter(process.stdout.readline, ''):
        yield line.strip()

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
            if not os.path.exists(fname):
                ret = f(*args, **kwargs)
                with open(fname, 'wb') as fptr:
                    pickle.dump(ret, fptr, pickle.HIGHEST_PROTOCOL)
            with open(fname, 'rb') as fptr:
                return pickle.load(fptr)

        def cache_exists(*args, **kwargs):
            k = _get_key(f, version, args, kwargs)
            fname = os.path.join(dir, f.__name__ + ':' + k + '.pickle')
            return os.path.exists(fname)

        setattr(wrapper, 'cache_exists', cache_exists)

        return wrapper
    return dec

def makedirs(directory):
    try:
        os.makedirs(directory)
    except Exception, e:
        if 'File exists' not in str(e):
            raise

def make_movie(directory, pattern='frame_%?%?%?%?%?.png', framerate=15, scale=None, verbose=False):
    last_dir = filter(bool, directory.split('/'))[-1]
    movie_path = '%s/%s_out.mp4' % (directory, last_dir)
    print 'Saving movie to %s/%s_out.mp4' % (directory, last_dir)
    cmd = ['/usr/bin/ffmpeg', '-framerate', str(framerate), 
            '-f', 'image2',
            '-pattern_type', 'glob',
            '-i', '%s/%s' % (directory, pattern), 
            '-f', 'mp4',
            '-vf', 'format=yuv420p',
            '-c:v', 'libx264', 
            '-r', '30', 
            '-crf', '0',
            ]
    if scale is not None:
        cmd += ['-vf', 'scale=%s' % scale]
    if not verbose:
        cmd += ['-loglevel', 'quiet']
    cmd += [movie_path, '-y']
    print ' '.join(cmd)
    run(cmd, capture_stdout=False, print_stdout=True)
    return movie_path

def _tmpf(*args, **kwargs):
    return tempfile.mkstemp(*args, **kwargs)[1]

@contextlib.contextmanager
def tmpf(*args, **kwargs):
    fname = _tmpf(*args, **kwargs)

    try:
        yield fname
    finally:
        os.remove(fname)
