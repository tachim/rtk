import collections
import functools
import matplotlib.pyplot as plt
import time
import timing

import atexit

def plot(x, y, title=None, xlabel=None, ylabel=None):
    plt.plot(x, y)
    
    if title is not None:
        plt.title(title)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.show()

_suppress_plots = False
_rt_plot_state = {}
_last_plot_time = 0
_plot_start = None
_n_plots = 0

def _subsample(lis, frac):
    stride = max(1, int(frac * len(lis)))
    return lis[::stride]

RTPlotState = collections.namedtuple('RTPlotState',
        ('x', 'y', 'xbuf', 'ybuf', 'line', 'n_so_far'))

def _get_ax(i):
    return plt.gcf().add_subplot(_n_plots, 1, i)

def _clear_bufs():
    for key, state in _rt_plot_state.iteritems():
        new_state = _subsample(zip(state.xbuf, state.ybuf), 0.1)
        state.x.extend([x for (x, y) in new_state])
        state.y.extend([y for (x, y) in new_state])
        del state.xbuf[:]
        del state.ybuf[:]

        state.line.set_xdata(state.x)
        state.line.set_ydata(state.y)

    for i in xrange(1, _n_plots+1):
        _get_ax(i).relim()
        _get_ax(i).autoscale_view(tight=True, scalex=True, scaley=True)
        _get_ax(i).legend(loc='upper left')

    plt.pause(0.1)

def _init_plot(n_plots):
    global _n_plots, _plot_start, _rt_ax
    _n_plots = n_plots
    fig = plt.gcf()
    _plot_start = time.time()
    plt.ion()
    plt.show()

class SuppressPlots(object):
    def __init__(self, should_suppress=True):
        self.should_suppress = should_suppress

    def __enter__(self):
        global _suppress_plots
        if self.should_suppress:
            self.old = _suppress_plots
            _suppress_plots = True

    def __exit__(self, *args):
        global _suppress_plots
        if self.should_suppress:
            _suppress_plots = self.old

def _wrap_pyplot(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RuntimeError, e:
            if 'DISPLAY' not in str(e):
                raise
    return wrapper

@_wrap_pyplot
def reset_rt_plot():
    global _rt_plot_state, _plot_start, _n_plots
    _rt_plot_state = {}
    _plot_start = None
    _n_plots = 0
    plt.gcf().clf()

@_wrap_pyplot
def plot_rt_point(key, y, plot_ind=1, x=None):
    if _suppress_plots:
        return

    fig = plt.gcf()

    assert _n_plots > 0
    assert plot_ind <= _n_plots

    if key not in _rt_plot_state:
        _rt_plot_state[key] = RTPlotState(
                [], [], [], [], 
                _get_ax(plot_ind).plot([], [], marker='.', label=key)[0],
                [0])

    plot_state = _rt_plot_state[key]
    x = x if x is not None else time.time() - _plot_start
    plot_state.xbuf.append(x)
    plot_state.ybuf.append(y)
    plot_state.n_so_far[0] += 1

    if timing._register_exec(__name__, 'plot', 1):
        _clear_bufs()

def _finish_plot():
    if _n_plots > 0:
        print 'Done. Exit plot to exit program.'
        _clear_bufs()
        plt.ioff()
        plt.show()

atexit.register(_finish_plot)


#######################################################
# Gaussians
# from http://www.nhsilbert.net/source/2014/06/bivariate-normal-ellipse-plotting-in-python/
#######################################################

def plot_cov_ellipse(cov, pos, volume=.5, ax=None, fc='none', ec=[0,0,0], a=1, lw=2):
    import numpy as np
    from scipy.stats import chi2
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse

    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:,order]

    ax = ax or plt.gca()

    vals, vecs = eigsorted(cov)
    theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))

    kwrg = {'facecolor':fc, 'edgecolor':ec, 'alpha':a, 'linewidth':lw}

    # Width and height are "full" widths, not radius
    width, height = 2 * np.sqrt(chi2.ppf(volume,2)) * np.sqrt(vals)
    ellip = Ellipse(xy=pos, width=width, height=height, angle=theta, **kwrg)
    ax.add_artist(ellip)
