import argparse as ap
from collections import defaultdict as dd
import itertools
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import time

from astropy.io import ascii

import rtk

def process_keys(args_keys, agg_key, cmp_key, result_keys):
    assert agg_key in args_keys and cmp_key in args_keys

    stats_keys = sorted([k for k in args_keys if k != agg_key and k != cmp_key])
    stats_keys.append(cmp_key)

    ret = stats_keys[:]
    ret.extend(sum(
        [[k + '_mean', k + '_std'] 
         if isinstance(k, basestring) else 
         ['result[%d]_mean' % k, 'result[%d]_std' % k] 
         for k in result_keys],
        []))
    return stats_keys, ret

def mean(args, results):
    results = np.array(results)
    if args.log_space:
        return rtk.m.logsumexp(results) - np.log(results.shape[0])
    else:
        return results.mean()

def std(args, results):
    results = np.array(results)
    if args.log_space:
        log_mean = mean(args, results)
        return np.sqrt(sum((r - log_mean) ** 2 for r in results) / results.shape[0])
    else:
        return results.std()

def print_results(args, colnames, stats):
    colnames = colnames + ['n_samples']
    colvals = [[] for _ in xrange(len(colnames))]

    kvs = sorted(rtk.itr.iter_nested_d(stats))

    for keys, val in kvs:
        i = 0
        for k in keys:
            colvals[i].append(k)
            i += 1
        n_results_cols = len(val[0])
        for j in xrange(n_results_cols):
            colvals[i].append(round(mean(args, map(rtk.itr.ig(j), val)), 3))
            i += 1
            colvals[i].append(round(std(args, map(rtk.itr.ig(j), val)), 3))
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
    parser.add_argument('experiment_ids', type=str)
    parser.add_argument('agg_key', type=str)
    parser.add_argument('cmp_key', type=str)
    parser.add_argument('result_keys', type=str)
    args = parser.parse_args()

    result_keys = args.result_keys.split(',')
    for i in xrange(len(result_keys)):
        try: result_keys[i] = int(result_keys[i])
        except: pass

    experiment_ids = []
    for experiment_id in args.experiment_ids.split(','):
        if experiment_id == 'last':
            experiment_id = rtk.dist.db.last_experiment()
        experiment_ids.append(experiment_id)
        print '%s: %s' % (experiment_id, rtk.dist.db.fetch_title(experiment_id))

        complete, started = rtk.dist.db.completion_counts(experiment_id)
        while complete < int(0.85 * started):
            print '%d complete out of %d' % (complete, started)
            time.sleep(5)
            complete, started = rtk.dist.db.completion_counts(experiment_id)

    print 'Analyzing logs for %d results' % complete

    stats = None
    stats_keys, all_columns = None, None
    keysets = set()
    for f_args, duration, result in itertools.chain(*
            [rtk.dist.db.iter_results(experiment_id)
                for experiment_id in experiment_ids]):
        if stats is None:
            stats_keys, all_columns = process_keys(f_args.keys(), args.agg_key, args.cmp_key, result_keys)
            stats = rtk.itr.dd(list, len(stats_keys))

        keys = [f_args[k] for k in stats_keys]
        keysets.add(tuple(keys))

        d = rtk.itr.ig(*keys[:-1])(stats)
        d[keys[-1]].append([result[result_key] for result_key in result_keys])

    print_results(args, all_columns, stats)

if __name__ == '__main__':
    rtk.debug.wrap(main)()
