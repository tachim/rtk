import argparse as ap
from collections import defaultdict as dd
import os
import matplotlib.pyplot as plt
import numpy as np
import random

import rtk

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('experiment_id', type=str)
    parser.add_argument('trial_id', type=int)
    args = parser.parse_args()

    directory, function, arguments = \
            rtk.dist.db.fetch_args(args.experiment_id, args.trial_id)
    import sys
    sys.path.append(directory)
    module_name, function_name = function.split('.')
    module = __import__(module_name)
    rtk.dist.db.mark_start(args.experiment_id, args.trial_id)

    with rtk.dist.mgr.Params(**arguments):
        result = getattr(module, function_name)()
    rtk.dist.db.mark_done(args.experiment_id, args.trial_id, result)

if __name__ == '__main__':
    rtk.debug.wrap(main)()
