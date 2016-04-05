import collections
import heapq
import numpy as np
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

def a_star_sample_convex(log_f, lower_bound, upper_bound):
    """ A* sampling for 1D unnormalized distributions f that are convex. """
    _cache = {}

    def conditional_log_mu(p):
        if p not in _cache:
            _cache[p] = log_f(p)
        return _cache[p]

    def M((lb, ub)):
        return max(log_f(lb), log_f(ub))

    def sample_g((lb, ub), trunc=None):
        mu = np.log(ub - lb)
        if trunc is None:
            return mu - np.log(-np.log(np.random.random()))
        else:
            return mu - np.log(np.exp(-trunc + mu) - np.log(np.random.random()))

    def sample_nu((lb, ub)):
        return lb + (ub - lb) * np.random.random()

    pq = []
    push = lambda (weight, g_val, bounds): heapq.heappush(pq, (-weight, g_val, bounds))
    def pop():
        weight, g_val, bounds = heapq.heappop(pq)
        return -weight, g_val, bounds

    bounds = (lower_bound, upper_bound)
    g_val = sample_g(bounds)
    push( (g_val + M(bounds), g_val, bounds) )

    LB = -1e8
    best_sample = None

    n_rounds = 0

    while pq:
        n_rounds += 1
        if n_rounds > 200:
            assert False

        weight, region_g_val, bounds = pop()
        if weight < LB:
            break

        sample = sample_nu(bounds)
        if region_g_val + conditional_log_mu(sample) > LB:
            LB = region_g_val + conditional_log_mu(sample)
            best_sample = sample

        lb, ub = bounds
        mid = lb + (ub - lb) * 0.5
        l, r = (lb, mid), (mid, ub)

        for part in (l, r):
            part_g_val = sample_g(part, region_g_val)
            if part_g_val + M(part) > LB:
                push((part_g_val + M(part), part_g_val, part))

    return best_sample


