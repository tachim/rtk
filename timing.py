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

class Logger(object):
    def __init__(self, name, print_every=1):
        self.name = name
        self.print_every = print_every

    def __enter__(self):
        assert self.name not in _timestamps
        _timestamps[self.name] = time.time()

    def __exit__(self, typ, val, tb):
        duration = time.time() - _timestamps[self.name]
        del _timestamps[self.name]
        t = _timings[self.name]
        t[0] = t[0] * t[1] / (t[1] + 1) + duration / (t[1] + 1)
        t[1] = t[1] + 1

        if int(t[1] - 1) % self.print_every == 0:
            print '<%s> over %d calls: %.4f. Last call: %.4f' % (
                    self.name, t[1], t[0], duration)
