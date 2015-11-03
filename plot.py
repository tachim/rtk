import matplotlib.pyplot as plt

def plot(x, y, title=None, xlabel=None, ylabel=None):
    plt.plot(x, y)
    
    if title is not None:
        plt.title(title)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.show()
