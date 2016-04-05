import matplotlib.pyplot as plt

def largify():
    plt.tick_params(axis='both', labelsize=30)
    plt.gcf().set_size_inches(30, 10)

def u(d, **kwargs):
    for k, v in kwargs.iteritems():
        if k not in d:
            d[k] = v

def title(*args, **kwargs):
    u(kwargs, fontsize=30)
    plt.title(*args, **kwargs)

def legend(*args, **kwargs):
    u(kwargs, prop=dict(size=30))
    plt.legend(*args, **kwargs)

def plot(*args, **kwargs):
    u(kwargs, linewidth=5)
    u(kwargs, markersize=30)
    plt.plot(*args, **kwargs)

def xlabel(*args, **kwargs):
    u(kwargs, fontsize=30)
    plt.xlabel(*args, **kwargs)

def ylabel(*args, **kwargs):
    u(kwargs, fontsize=30)
    plt.ylabel(*args, **kwargs)
