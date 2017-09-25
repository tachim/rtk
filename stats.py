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
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

def annotate(img, text):
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(
            "/usr/local/lib/python2.7/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSansMono-Bold.ttf", 
            16)
    draw.text((0, 0), text,(0,255,0),font=font)
    return np.array(img)

def get_plt_img():
    fig = plt.gcf()
    fig.savefig('/tmp/img.png', dpi=120)
    return np.array(Image.open('/tmp/img.png'))[..., :3]

class RollingImageHistory(object):
    def __init__(self):
        self.imgs = []

    def add_img(self, itr, img):
        assert itr % 100 == 0
        self.imgs.append((itr, annotate(img, 'itr %d' % itr)))

    def rolling_imgs(self):
        return [img for _, img in self.imgs[::-1]]

    def generate_rolling(self):
        return np.hstack([img for _, img in self.imgs[::-1]])

class Reporter(object):
    def __init__(self, env, 
                  plot_suffix=None, url='http://192.168.7.67', 
                  port=8097, ratelimit_sec=10,
                  default_outlier_percentile=None,
                  ):
        self.env = env
        self.vis = visdom.Visdom(url, port=port, env=self.env)
        self.stats = collections.defaultdict(list)
        self.ratelimit_sec = ratelimit_sec
        self.plot_suffix = plot_suffix

        self.init_set = set()
        self.outlier_percentile = {}
        self.default_outlier_percentile = default_outlier_percentile
        self.k_to_window = {}

    def set_outlier_percentile(self, k, p):
        self.outlier_percentile[k] = p

    def title(self, k):
        return k if self.plot_suffix is None else k + '_' + self.plot_suffix

    def init(self, k):
        if k in self.init_set: return
        self.vis.line(
                np.array([0]), np.array([0]), 
                win=self.title(self.k_to_window[k]), 
                opts=dict(title=self.title(k)))
        self.init_set.add(k)

    def flush(self):
	import rtk
        if not rtk.timing._register_exec('h.vis.vdom.reporter', self.env, self.ratelimit_sec):
            return

        for k, vals in self.stats.iteritems():
            self.init(k)

            x, y = np.arange(len(vals)), np.array(vals)
            opts = {}
            outlier_percentile = self.outlier_percentile.get(k, self.default_outlier_percentile)
            if outlier_percentile is not None:
                thresh = np.percentile(y, outlier_percentile)
                opts['ytickmin'] = int(y.min())
                opts['ytickmax'] = int(thresh)

            opts['legend'] = False

            self.vis.updateTrace(
                    Y=y, X=x, 
                    win=self.title(self.k_to_window[k]), name=self.title(k), 
                    append=False,
                    opts=opts,
                    )

    def _transform(self, val):
        if isinstance(val, Variable):
            val = val.data
        if type(val) in (torch.cuda.FloatTensor, torch.FloatTensor):
            val = val.cpu().numpy().copy()
        if isinstance(val, np.ndarray):
            val = val.squeeze()
        return val

    def _transform_img(self, img):
        img = np.uint8((self._transform(img).astype(np.float32) + 1) * 128)
        if len(img.shape) > 2:
            img = img.transpose(1, 2, 0)
        return img

    def report(self, key, val, win=None):
        self.stats[key].append(self._transform(val))
        self.k_to_window[key] = win or key
        self.flush()

    def close(self, win):
        k = win if self.plot_suffix is None else win + '_' + self.plot_suffix
        self.vis.close(k)

    def text(self, key, txt):
        self.vis.text(txt, win=self.title(key), opts=dict(title=self.title(key)))

    def image(self, key, img):
        if not isinstance(img, np.ndarray):
            img = self._transform_img(img)
        if len(img.shape) > 2:
            img = img.transpose(2, 0, 1)
        self.vis.image(img, win=self.title(key), opts=dict(title=self.title(key)))

    def images(self, key, imgs):
        if not isinstance(imgs[0], np.ndarray):
            imgs = map(self._transform_img, imgs)
        imgs = [img.transpose(2, 0, 1) if len(img.shape) > 2 else img for img in imgs]
        self.vis.images(imgs, win=self.title(key), opts=dict(title=self.title(key)))

    def heatmap(self, k, heatmap, xmin=None, xmax=None):
        heatmap = self._transform(heatmap)
        heatmap = heatmap[::-1]
        assert isinstance(heatmap, np.ndarray)
        opts = dict(title=self.title(k))
        if xmin is not None: opts['xmin'] = xmin
        if xmax is not None: opts['xmax'] = xmax
        self.vis.heatmap(heatmap, win=self.title(k), opts=opts)
