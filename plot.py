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

_rt_ax = None
_rt_plot_state = {}
_last_plot_time = 0
_plot_start = None

def _subsample(lis, frac):
    stride = max(1, int(frac * len(lis)))
    return lis[::stride]

RTPlotState = collections.namedtuple('RTPlotState',
        ('x', 'y', 'xbuf', 'ybuf', 'line', 'n_so_far'))

def _clear_bufs():
    for key, state in _rt_plot_state.iteritems():
        new_state = _subsample(zip(state.xbuf, state.ybuf), 0.1)
        state.x.extend([x for (x, y) in new_state])
        state.y.extend([y for (x, y) in new_state])
        del state.xbuf[:]
        del state.ybuf[:]

        state.line.set_xdata(state.x)
        state.line.set_ydata(state.y)

    _rt_ax.relim() 
    _rt_ax.autoscale_view(True,True,True)
    plt.pause(0.1)

def _init_plot():
    global _plot_start, _rt_ax
    fig = plt.gcf()
    _plot_start = time.time()
    plt.ion()
    plt.show()
    _rt_ax = fig.add_subplot(111)

def plot_rt_point(key, y, x=None):
    fig = plt.gcf()

    if _rt_ax is None:
        _init_plot()

    if key not in _rt_plot_state:
        _rt_plot_state[key] = RTPlotState(
                [], [], [], [], 
                _rt_ax.plot([], [], marker='.', label=key)[0],
                [0])
        _rt_ax.legend()

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
    if _rt_ax is not None:
        print 'Done. Exit plot to exit program.'
        _clear_bufs()
        plt.ioff()
        plt.show()

atexit.register(_finish_plot)
