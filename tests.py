import numpy as np

def assert_eq(a, b, eps=0):
    assert np.all(np.abs(a - b) < eps), ('%s not equal to %s with eps=%f' % (a, b, eps))
