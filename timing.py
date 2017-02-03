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

def reset_all():
    _timings.clear()

class Logger(object):
    def __init__(self, name, print_every=10, reset_timing=False, n_expected=None):
        self.name = name
        self.print_every = print_every
        self.n_expected = n_expected
        if reset_timing:
            reset(self.name)

    def __enter__(self):
        assert self.name not in _timestamps
        _timestamps[self.name] = time.time()

    def __exit__(self, typ, val, tb):
        duration = time.time() - _timestamps[self.name]
        del _timestamps[self.name]
        t = _timings[self.name]
        t[0] = t[0] * t[1] / (t[1] + 1) + duration / (t[1] + 1)
        t[1] = t[1] + 1

        if _register_exec(__name__, 'logger%s' % self.name, self.print_every):
            print '<%s> over %d calls: %.4f. Last call: %.4f. ' % (
                    self.name, t[1], t[0], duration),
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
