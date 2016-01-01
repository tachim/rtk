import numpy as np
import random

def ones(shape):
    return np.random.randint(0, 2, shape)

def shuffle(a):
    if isinstance(a, list):
        ret = a[:]
        random.shuffle(ret)
        return ret
    else:
        assert False
