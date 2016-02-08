import numpy as np
import random

def seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def ones(shape):
    return np.random.randint(0, 2, shape)

def shuffle(a):
    if isinstance(a, list):
        ret = a[:]
        random.shuffle(ret)
        return ret
    else:
        assert False
