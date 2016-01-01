import numpy as np

def generate(n, strength=3):
    W = np.random.random((n, n)) * 2 - 1
    W = np.triu(W)
    np.fill_diagonal(W, 0)
    f = np.random.random((n,)) * 2 -1 
    return W * strength, f * strength

def write_fg(W, f, filename):
    assert filename.endswith('.fg')
    n = W.shape[0]

    valid_pair_factors = []
    for i in xrange(n):
        for j in xrange(n):
            if W[i, j] != 0:
                valid_pair_factors.append((i, j))
    valid_single_factors = range(n)

    with open(filename, 'w') as f_out:
        f_out.write('%d\n\n' % (len(valid_pair_factors) + len(valid_single_factors)))

        for i in valid_single_factors:
            f_out.write('1\n%d\n2\n2\n' % i)
            f_out.write('0 %.20f\n1 %.20f\n' % (np.exp(-f[i]), np.exp(f[i])))

        for i, j in valid_pair_factors:
            f_out.write('2\n') # number of variables in factor
            f_out.write('%d %d\n' % (i, j)) # variable labels
            f_out.write('2 2\n') # number of assignments for each variable
            f_out.write('4\n') # number of nonempty entries in factor table
            pos_prob = np.exp(W[i, j])
            neg_prob = np.exp(-W[i, j])
            f_out.write('0 %.20f\n1 %.20f\n2 %.20f\n3 %.20f\n' % (pos_prob, neg_prob, neg_prob, pos_prob))
