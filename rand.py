import numpy as np
import random
import string

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

def rand_string(length):
    return ''.join([
        random.choice(string.ascii_letters)
        for _ in xrange(length)
        ])
