import subprocess as sp
import multiprocessing as mp
import numpy as np
import random
import time
import traceback
import sys

import timing

def wrapper_fcn(arg_str):
    import dill
    fn, (i, args_kwargs) = dill.loads(arg_str)
    seed = int(random.random() * 100000)
    np.random.seed(seed)
    random.seed(seed)
    try:
        if False:
            print '.',; sys.stdout.flush()
        ret = fn(*args_kwargs[0], **args_kwargs[1])
        return i, ret
    except:
        print 'EXCEPTION WITH ARGS:', (str(fn) + str(args_kwargs))[:100]
        traceback.print_exc()
        sys.stdout.flush()
        return i, None

def process_args_kwargs(args_kwargs):
    if isinstance(args_kwargs[0], tuple) and \
            type(args_kwargs[0][0]) in (list, tuple) and \
            type(args_kwargs[0][1]) in (dict,):
        return args_kwargs
    elif isinstance(args_kwargs[0], dict):
        return [([], a) for a in args_kwargs]
    else:
        return [([a], {}) for a in args_kwargs]

def pmap(fn, args_kwargs, verbose=True, super_verbose=False, n_procs=None, pool=None):
    """ Multiprocessing abstraction that includes a progress meter.
        Usage:
            def foo(x): return x * 2
            pmap(foo, [([1], {}), ([2], {})]) => [2, 4]

    """

    sp.call('pip install dill'.split())
    import dill

    global _pool_state
    try:
        args_kwargs = process_args_kwargs(args_kwargs)
        n_procs = n_procs or mp.cpu_count() - 1
        if verbose:
            print 'Using', n_procs, 'processes.'
        #mp.freeze_support()
        p = pool or mp.Pool(n_procs)
        ret = [None] * len(args_kwargs)

        processed_args = [(fn, (i, a_k)) for i, a_k in enumerate(args_kwargs)]
        processed_args = map(dill.dumps, processed_args)

        start_time = time.time()

        for job_ind, (arg_ind, result) in \
                enumerate(p.imap_unordered(wrapper_fcn, processed_args, chunksize=1)):

            n_completed = job_ind + 1
            avg_time = (time.time() - start_time) / n_completed
            num_remaining = len(args_kwargs) - n_completed
            eta = avg_time * num_remaining

            if verbose and timing._register_exec(__file__, 'pmap', 20):
                print '\n>>>>>>>>>>> PROGRESS:', job_ind+1, '/', len(args_kwargs), 'done. ETA:', eta
            ret[arg_ind] = result

            if super_verbose:
                print 'Args remaining:', [arg for i, arg in enumerate(args_kwargs) if ret[i] == None]
        if pool is None:
            p.terminate()
            p.join()
            del p
        if verbose:
            print '\n>>>>>>>>>>> DONE.', job_ind+1, '/', len(args_kwargs)
        return ret
    except Exception, e:
        # If there was an exception thrown above, then re-run it single-threaded until we hit
        # the exception so we can raise it with the right stack trace.
        print 'Hit exception in parallel run:', str(e)
        print 'Re-running single-threaded.'
        ret = []
        for i, (args, kwargs) in enumerate(args_kwargs):
            if verbose:
                print '>>>>>>>>>>> SINGLE-THREAD PROGRESS:', i+1, '/', len(args_kwargs), 'done'
            ret.append(fn(*args, **kwargs))

        # Throw the original if we didn't hit any exception in the single-threaded execution
        raise
        return ret
