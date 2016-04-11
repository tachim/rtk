import numpy as np
import os
import tempfile

class MRFWriter(object):
    def __init__(self, theta, remove=True):
        self.theta = theta
        self.remove = remove

    def __enter__(self):
        _, self.filename = tempfile.mkstemp(suffix='.fg')
        write_fg(self.theta, self.filename)
        return self

    def __exit__(self, typ, val, tb):
        if self.remove:
            os.remove(self.filename)

def write_fg(theta, filename):
    assert filename.endswith('.fg')
    assert np.all(np.tril(theta, k=-1) == 0), 'Nonzero weights below diagonal not supported.'

    n = theta.shape[0]

    valid_pair_factors = []
    for i in xrange(n):
        for j in xrange(i+1, n):
            if theta[i, j] != 0:
                valid_pair_factors.append((i, j))
    valid_single_factors = range(n)

    with open(filename, 'w') as f_out:
        f_out.write('%d\n\n' % (len(valid_pair_factors) + len(valid_single_factors)))

        for i in valid_single_factors:
            f_out.write('1\n%d\n2\n2\n' % i)
            f_out.write('0 %.20f\n1 %.20f\n\n' % (1, np.exp(theta[i, i])))

        for i, j in valid_pair_factors:
            f_out.write('2\n') # number of variables in factor
            f_out.write('%d %d\n' % (i, j)) # variable labels
            f_out.write('2 2\n') # number of assignments for each variable
            f_out.write('4\n') # number of nonempty entries in factor table
            neg_prob = 1
            pos_prob = np.exp(theta[i, j])
            f_out.write('0 %.20f\n1 %.20f\n2 %.20f\n3 %.20f\n\n' % (1, 1, 1, pos_prob))

    print 'Wrote MRF to', filename

def read_uai(filename):
    n = None
    n_factors = None
    theta = None
    factor_inds = []

    with open(filename, 'r') as f:
        lineno = [0]

        def _rl():
            l = f.readline().strip()
            lineno[0] += 1
            while not l:
                l = f.readline().strip()
                lineno[0] += 1
            return l

        assert _rl() == 'MARKOV'
        n = int(_rl())
        _rl()
        n_factors = int(_rl())

        theta = np.zeros((n, n))
        
        for _ in xrange(n_factors):
            l = map(int, _rl().split())
            assert all(e < n for e in l[1:])
            factor_inds.append(l[1:])

        for factor in factor_inds:
            if len(factor) == 2:
                assert int(_rl()) == 4
                for _ in xrange(3): _rl()
                theta[factor[0], factor[1]] = np.log(float(_rl()))
            elif len(factor) == 1:
                assert int(_rl()) == 2
                assert float(_rl()) == 1
                theta[factor[0], factor[0]] = np.log(float(_rl()))
            else:
                assert False
    return theta
