import multiprocessing as mp
import numpy as np
import random
import time

def wrapper_fcn((fn, (i, args_kwargs))):
    seed = int(random.random() * 100000)
    np.random.seed(seed)
    random.seed(seed)
    return i, fn(*args_kwargs[0], **args_kwargs[1])

def pmap(fn, args_kwargs, verbose=True, super_verbose=False, n_procs=None):
    """ Multiprocessing abstraction that includes a progress meter.
        Usage:
            def foo(x): return x * 2
            pmap(foo, [([1], {}), ([2], {})]) => [2, 4]

    """
    try:
        n_procs = n_procs or mp.cpu_count()
        p = mp.Pool(n_procs)
        ret = [None] * len(args_kwargs)

        processed_args = [(fn, (i, a_k)) for i, a_k in enumerate(args_kwargs)]

        start_time = time.time()

        for job_ind, (arg_ind, result) in \
                enumerate(p.imap_unordered(wrapper_fcn, processed_args, chunksize=1)):

            n_completed = job_ind + 1
            avg_time = (time.time() - start_time) / n_completed
            num_remaining = len(args_kwargs) - n_completed
            eta = avg_time * num_remaining

            if verbose:
                print '>>>>>>>>>>> PROGRESS:', job_ind+1, '/', len(args_kwargs), 'done. ETA:', eta
            ret[arg_ind] = result

            if super_verbose:
                print 'Args remaining:', [arg for i, arg in enumerate(args_kwargs) if ret[i] == None]
        p.close()
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
