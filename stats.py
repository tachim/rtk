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
        self.w = 0.0

    def __enter__(self): return self
    def __exit__(self, *args): return

    def report(self, x, weight=1):
        if self.w == 0:
            self.mu = x
            self.var = 0
        else:
            mu_new = self.mu * (self.w / (self.w + weight)) + x / (self.w + weight)
            delta = mu_new - self.mu
            var_new = self.var + self.w * delta ** 2 + weight * (x - mu_new) ** 2
            self.mu = mu_new
            self.var = var_new
        self.w += weight

def _is_dict(d):
    return isinstance(d, dict) or isinstance(d, collections.defaultdict)

def aggregate_leaves(d, agg):
    return dict(
            (k, aggregate_leaves(v, agg) 
                if _is_dict(v)
                else agg(v))
            for k, v in d.iteritems())
