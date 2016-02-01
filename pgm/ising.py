import numpy as np

def generate(n, strength=3):
    # create W and remove everything including and below the diagonal
    W = np.random.random((n, n)) * 2 - 1
    W = np.triu(W, k=1)
    f = np.random.random((n,)) * 2 -1 
    return W * strength, f * strength

def write_uai(W, f, filename):
    assert filename.endswith('.uai')
    n = W.shape[0]

    valid_pair_factors = []
    for i in xrange(n):
        for j in xrange(n):
            if W[i, j] != 0:
                valid_pair_factors.append((i, j))
    valid_single_factors = range(n)

    with open(filename, 'w') as f_out:
        lines = []
        lines.append('MARKOV')
        lines.append('%d' % n)
        lines.append(' '.join(map(str, [2] * n)))
        lines.append(str(len(valid_pair_factors) + len(valid_single_factors)))

        for var in valid_single_factors:
            lines.append('1 %d' % var)

        for i, j in valid_pair_factors:
            lines.append('2 %d %d' % (i, j))

        for i in valid_single_factors:
            lines.append('2')
            lines.append('%.20f %.20f\n' % (np.exp(-f[i]), np.exp(f[i])))

        for i, j in valid_pair_factors:
            lines.append('4') # number of variables in factor
            pos_prob = np.exp(W[i, j])
            neg_prob = np.exp(-W[i, j])
            lines.append('%.20f%.20f\n%.20f\n%.20f\n' % (pos_prob, neg_prob, neg_prob, pos_prob))

        f_out.write('\n'.join(lines))

    print 'Wrote Ising model to', filename

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

    print 'Wrote Ising model to', filename