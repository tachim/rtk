import collections
import time

_means_counts = collections.defaultdict(lambda: [0., 0.])

def reset(k):
    _means_counts[k] = [0., 0.]

def report(k, val, print_every=1):
    mu, ct = _means_counts[k]
    _means_counts[k] = [mu * ct / (ct + 1) + val / (ct + 1), ct + 1]
    if (ct + 1) % print_every == 0:
        print '<%s> mean over %d calls: %.4f.' % (k, ct+1, _means_counts[k][0])

class OnlineMoments(object):
    # Keeps track of mean and variance in an online way
    def __init__(self):
        self.mu = None
        self.var = None
        self.n = 0.0

    def __enter__(self): return self
    def __exit__(self, *args): return

    def report(self, x):
        if self.n == 0:
            self.mu = x
            self.var = 0
        else:
            mu_new = self.mu * (self.n / (self.n + 1)) + x / (self.n + 1)
            delta = mu_new - self.mu
            var_new = self.var + self.n * delta ** 2 + (x - mu_new) ** 2
            self.mu = mu_new
            self.var = var_new
        self.n += 1

