import numpy as np
import os
import tempfile

import scipy.io
import rtk

def load_rbm(filename):
    base_name = os.path.basename(filename)
    if filename.endswith('.uai'):
        return None, rtk.pgm.mrf.read_uai(filename), None
    elif base_name.startswith('demo') and base_name.endswith('.mat'):
        M = scipy.io.loadmat(filename)
        wvh1 = M['w1_vishid']
        #wh1h2 = M['w2']
        h1b = M['h1_biases']
        h2b = M['h2_biases']
        nvis, nh1 = wvh1.shape
        
        _f = np.hstack((
            h1b, 
            np.zeros((1, nvis)),
            ))[0]
        assert _f.shape == (nvis + nh1,)

        _theta = np.zeros((nvis+nh1, nvis+nh1))
        _theta[:nh1, nh1:] = wvh1.T
        #_theta += _theta.T
        np.fill_diagonal(_theta, _f)
        return nh1, _theta, 0
    else:
        if filename.endswith('.dat'):
            with open(filename, 'r') as f:
                lines = [map(float, filter(bool, l.strip().split(','))) for l in f]
            hidbiases = np.array(lines[0])[None, :]
            visbiases = np.array(lines[1])[None, :]
            vishid = np.array(lines[2:]).T
        elif filename.endswith('.mat'):
            m = scipy.io.loadmat(filename)
            visbiases = m['visbiases']
            hidbiases = m['hidbiases']
            vishid = m['vishid']
        else:
            assert False, 'Don\'t know how to read the file.'
        nvisible = visbiases.shape[1]
        nh1 = hidbiases.shape[1]
        assert vishid.shape == (nvisible, nh1)
        _f = np.hstack((hidbiases , visbiases))[0]
        assert _f.shape == (nvisible + nh1,)
        _W = vishid
        assert _W.shape == (nvisible, nh1)
        
        print nvisible, " visible units. ", nh1, " hidden."
        n = nvisible + nh1

        _theta = np.diag(_f)
        for i in xrange(nh1):
            for j in xrange(nh1, n):
                _theta[i, j] = vishid[j - nh1, i]
        return nh1, _theta, 0
