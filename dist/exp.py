#!/usr/bin/env python

import argparse as ap
from collections import defaultdict as dd
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import datetime

import rtk

def log():
    for row in rtk.dist.db.query('''
        SELECT ets.experiment_id eid, ct, title, n_completed, n_jobs
        FROM (
            SELECT 
                experiment_id, 
                MIN(creation_timestamp) ct,
                SUM(if(result is not null, 1, 0)) n_completed,
                COUNT(1) n_jobs
            FROM results
            GROUP BY experiment_id
            ORDER BY ct ASC
        ) ets LEFT OUTER JOIN experiment_metadata emd
        ON ets.experiment_id = emd.experiment_id
        '''):
        eid = row['eid']
        creation_time = datetime.datetime.fromtimestamp(
                int(row['ct'] / 1e6)
                ).strftime('%Y-%m-%d %H:%M:%S')
        title = row['title']
        completion = '%d / %d' % (row['n_completed'], row['n_jobs'])
        print eid, creation_time, title, completion

def set_title(experiment_id, title):
    rtk.dist.db.set_title(experiment_id, title)

def rerun_failed(experiment_ids, walltime='00:10:00', ppn=1):
    cmds, ofiles = [], []

    for experiment_id, trial_id in rtk.dist.db.iter_failed_trials(experiment_ids):
        command = 'python %s %s %s' % (rtk.dist.mgr.runner_fname(), experiment_id, trial_id)
        outputfile = os.path.join(rtk.dist.config.output_dir, '%s_%s.log' % (experiment_id, trial_id))
        cmds.append(command)
        ofiles.append(outputfile)

    base_args = {
            'jobname': experiment_ids,
            'queue': 'atlas',
            'walltime': walltime,
            'ppn': ppn,
            'outputfile_dir': rtk.dist.config.output_dir,
            }
    rtk.dist.pbs.run(base_args, cmds, ofiles, force=True)

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-e', '--experiment_ids', type=str)
    parser.add_argument('-t', '--title', type=str)
    parser.add_argument('operation')
    args = parser.parse_args()

    if args.operation == 'log':
        log()

    elif args.operation == 'title':
        set_title(args.experiment_ids, args.title)

    elif args.operation == 'rerun':
        rerun_failed(args.experiment_ids)

    else:
        assert False

if __name__ == '__main__':
    rtk.debug.wrap(main)()
