import collections
import heapq
import numpy as np
import time
import scipy.misc
from PIL import Image

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
        return max(conditional_log_mu(lb), conditional_log_mu(ub))

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
        lb, ub = bounds
        if weight < LB:
            break

        sample = sample_nu(bounds)
        if region_g_val + conditional_log_mu(sample) > LB:
            LB = region_g_val + conditional_log_mu(sample)
            best_sample = sample

        if False: # debug assertion
            assert log_f(lb) >= log_f(sample) or log_f(ub) >= log_f(sample)

        mid = lb + (ub - lb) * 0.5
        l, r = (lb, mid), (mid, ub)
        assert lb >= lower_bound and ub <= upper_bound

        for part in (l, r):
            part_g_val = sample_g(part, region_g_val)
            if part_g_val + M(part) > LB:
                push((part_g_val + M(part), part_g_val, part))

    return best_sample

import torch
import torch.utils.data
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torchvision import datasets, transforms
import visdom

import collections

class Reporter(object):
    def __init__(self, env, plot_suffix=None, url='http://192.168.7.67', port=8097, ratelimit_sec=2):
        self.env = env
        self.vis = visdom.Visdom(url, port=port, env=self.env)
        self.stats = collections.defaultdict(list)
        self.ratelimit_sec = ratelimit_sec
        self.plot_suffix = plot_suffix

        self.init_set = set()

    def init(self, k):
        if k in self.init_set: return
        self.vis.line(np.array([0]), np.array([0]), win=k)
        self.init_set.add(k)

    def flush(self):
	import rtk
        if not rtk.timing._register_exec('h.vis.vdom.reporter', self.env, self.ratelimit_sec):
            return

        for k, vals in self.stats.iteritems():
            title = k if self.plot_suffix is None else k + '_' + self.plot_suffix
            self.init(k)
            self.vis.updateTrace(Y=np.array(vals), X=np.arange(len(vals)), win=k, name=title, append=False)

    def _transform(self, val):
        if isinstance(val, Variable):
            val = val.data
        if type(val) in (torch.cuda.FloatTensor, torch.FloatTensor):
            val = val.cpu().numpy().copy()
        if isinstance(val, np.ndarray):
            val = val.squeeze()
        return val

    def report(self, key, val):
        self.stats[key].append(self._transform(val))
        self.flush()

    def image(self, key, img):
        img = np.uint8((self._transform(img).astype(np.float32) + 1) * 128)
        #img = np.uint8(scipy.misc.imresize(img, (256, 256)))
        #img = Image.fromarray(img, mode='RGB')
        self.vis.image(img, win=key, opts=dict(title=key))
