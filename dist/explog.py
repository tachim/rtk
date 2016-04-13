import argparse as ap
from collections import defaultdict as dd
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import datetime

import rtk

def main():
    for row in rtk.dist.db.query('''
        SELECT ets.experiment_id eid, ct, title 
        FROM (
            SELECT experiment_id, MIN(creation_timestamp) ct
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
        print eid, creation_time, title

if __name__ == '__main__':
    rtk.debug.wrap(main)()
