import numpy as np
import random
import string
import contextlib

def seed(seed):
    random.seed(seed)
    np.random.seed(seed)

@contextlib.contextmanager
def seed_ctx(new_seed):
    curr_state = random.getstate()
    curr_state_np = np.random.get_state()

    seed(new_seed)
    yield

    random.setstate(curr_state)
    np.random.set_state(curr_state_np)

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

def choice(a):
    return a[np.random.randint(0, len(a))]
