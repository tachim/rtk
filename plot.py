import collections
import matplotlib.pyplot as plt
import time

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
        _get_ax(i).autoscale_view(True, True, True)
        _get_ax(i).legend()
    plt.pause(0.1)

def _init_plot():
    global _plot_start, _rt_ax
    fig = plt.gcf()
    _plot_start = time.time()
    plt.ion()
    plt.show()

def plot_rt_point(key, y, plot_ind=1, x=None):
    fig = plt.gcf()

    if _n_plots == 0:
        _init_plot()

    if key not in _rt_plot_state:
        global _n_plots
        _n_plots = max(plot_ind, _n_plots)

        _rt_plot_state[key] = RTPlotState(
                [], [], [], [], 
                _get_ax(plot_ind).plot([], [], marker='.', label=key)[0],
                [0])

    plot_state = _rt_plot_state[key]
    x = x if x is not None else time.time() - _plot_start
    plot_state.xbuf.append(x)
    plot_state.ybuf.append(y)
    plot_state.n_so_far[0] += 1

    global _last_plot_time
    if time.time() - _last_plot_time > 1:
        _clear_bufs()
        _last_plot_time = time.time()

def _finish_plot():
    if _n_plots > 0:
        print 'Done. Exit plot to exit program.'
        _clear_bufs()
        plt.ioff()
        plt.show()

atexit.register(_finish_plot)
