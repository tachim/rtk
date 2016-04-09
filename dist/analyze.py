import argparse as ap
from collections import defaultdict as dd
import os
import matplotlib.pyplot as plt
import numpy as np
import random

import rtk

def reorder_keys(args_keys, agg_key, cmp_key):
    assert agg_key in args_keys and cmp_key in args_keys

    ret = []
    ret.extend(sorted([k for k in args_keys if k != agg_key and k != cmp_key]))
    ret.append(cmp_key)
    ret.append(agg_key)
    return ret

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('experiment_id', type=str)
    parser.add_argument('agg_key', type=str)
    parser.add_argument('cmp_key', type=str)
    parser.add_argument('result_ind', type=int)
    args = parser.parse_args()

    experiment_id = args.experiment_id 
    if experiment_id == 'last':
        experiment_id = rtk.dist.db.last_experiment()

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

    for keys, val in rtk.itr.iter_nested_d(stats):
        print keys, np.array(val).mean()

if __name__ == '__main__':
    rtk.debug.wrap(main)()
