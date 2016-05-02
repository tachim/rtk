import numpy as np
import scipy.misc
import scipy.special

from rtk.tests import *

def binom(n, k):
    return scipy.special.binom(n, k)

logsumexp = scipy.misc.logsumexp

def mean_logsumexp(x):
    return logsumexp(x) - np.log(len(x))

def normalize_logprobs(log_probs):
    # Given n unnormalized log weights, return the normalized 
    # version of exp(log_probs). This involves a neat log-space
    # trick to prevent underflow.
    log_denom = logsumexp(log_probs)
    log_probs = log_probs - log_denom
    probs = np.exp(log_probs)
    assert not np.any(np.isnan(probs))
    return probs
