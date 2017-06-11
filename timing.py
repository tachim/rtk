__doc__ = """

Usage:

    import rtk
    with rtk.timing.Logger("Your key"):
        <your code>

"""

import collections
import time

_timings = collections.defaultdict(lambda: [0., 0.])
_timestamps = {}

def reset(k):
    _timings[k] = [0., 0.]
    del _timestamps[k]

def reset_all():
    _timings.clear()
    _timestamps.clear()
    _last_exec.clear()

class Logger(object):
    def __init__(self, name, print_every=10, reset_timing=False, n_expected=None, looping=False):
        self.name = name
        self.print_every = print_every
        self.n_expected = n_expected
        self.looping = looping
        self.duration = None
        if reset_timing:
            reset(self.name)

    def __enter__(self):
        assert self.looping or self.name not in _timestamps
        if self.looping and self.name in _timestamps:
            self.duration = time.time() - _timestamps[self.name]
        _timestamps[self.name] = time.time()

    def __exit__(self, typ, val, tb):
        if self.looping and self.duration is None:
            return
        elif not self.looping:
            self.duration = time.time() - _timestamps[self.name]
            del _timestamps[self.name]

        t = _timings[self.name]
        t[0] = t[0] * t[1] / (t[1] + 1) + self.duration / (t[1] + 1)
        t[1] = t[1] + 1

        if _register_exec(__name__, 'logger%s' % self.name, self.print_every):
            print '<%s> over %d calls: %.4f. Last call: %.4f. ' % (
                    self.name, t[1], t[0], self.duration),
            if self.n_expected is not None:
                n_completed = float(t[1])
                n_remaining = self.n_expected - n_completed
                time_remaining = t[0] * n_remaining
                
                print '%.4fs remaining.' % time_remaining,
            print

_last_exec = {}

def _register_exec(prefix, key, n_secs):
    k = prefix + '|' + key
    if _last_exec.get(k, 0) < time.time() - n_secs:
        _last_exec[k] = time.time()
        return True
    return False
