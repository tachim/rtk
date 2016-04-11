import argparse as ap
from collections import defaultdict as dd
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import time

from astropy.io import ascii

import rtk

def reorder_keys(args_keys, agg_key, cmp_key):
    assert agg_key in args_keys and cmp_key in args_keys

    ret = []
    ret.extend(sorted([k for k in args_keys if k != agg_key and k != cmp_key]))
    ret.append(cmp_key)
    ret.append(agg_key)
    return ret

def aggregate(args, results):
    results = np.array(results)
    if args.log_space:
        return rtk.m.logsumexp(results) - np.log(results.shape[0])
    else:
        return results.mean()

def print_results(args, colnames, stats):

    colnames = colnames + ['n_samples']
    colvals = [[] for _ in xrange(len(colnames))]

    for keys, val in rtk.itr.iter_nested_d(stats):
        i = 0
        for k in keys:
            colvals[i].append(k)
            i += 1
        colvals[i].append(aggregate(args, val))
        i += 1

        colvals[i].append(len(val))

    ascii.write(colvals, 
            Writer=ascii.FixedWidthTwoLine, 
            names=colnames,
            bookend=True, 
            delimiter='|',
            delimiter_pad=' ')

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('--log_space', action='store_true', default=False,
            help='Assume data is in log space when aggregating.')
    parser.add_argument('experiment_id', type=str)
    parser.add_argument('agg_key', type=str)
    parser.add_argument('cmp_key', type=str)
    parser.add_argument('result_ind', type=int)
    args = parser.parse_args()

    experiment_id = args.experiment_id 
    if experiment_id == 'last':
        experiment_id = rtk.dist.db.last_experiment()
        print 'Experiment is', experiment_id

    complete, started = rtk.dist.db.completion_counts(experiment_id)
    while complete < int(0.9 * started):
        print '%d complete out of %d' % (complete, started)
        time.sleep(5)
        complete, started = rtk.dist.db.completion_counts(experiment_id)

    print 'Analyzing logs for %d results' % complete

    stats = None
    ordered_keys = None
    keysets = set()
    for f_args, duration, result in rtk.dist.db.iter_results(experiment_id):
        if stats is None:
            ordered_keys = reorder_keys(f_args.keys(), args.agg_key, args.cmp_key)
            stats = rtk.itr.dd(list, len(ordered_keys)-1)

        keys = [f_args[k] for k in ordered_keys]
        keysets.add(tuple(keys[:-1]))

        d = rtk.itr.ig(*keys[:-2])(stats)
        d[keys[-2]].append(result[args.result_ind])

    print_results(args, ordered_keys, stats)

if __name__ == '__main__':
    rtk.debug.wrap(main)()
