import multiprocessing as mp

def wrapper_fcn((fn, (i, args_kwargs))):
    return i, fn(*args_kwargs[0], **args_kwargs[1])

def pmap(fn, args_kwargs, verbose=True):
    """ Multiprocessing abstraction that includes a progress meter.
        Usage:
            def foo(x): return x * 2
            pmap(foo, [([1], {}), ([2], {})]) => [2, 4]

    """
    p = mp.Pool(mp.cpu_count())
    ret = [None] * len(args_kwargs)

    processed_args = [(fn, (i, a_k)) for i, a_k in enumerate(args_kwargs)]

    for job_ind, (arg_ind, result) in \
            enumerate(p.imap_unordered(wrapper_fcn, processed_args, chunksize=1)):
        if verbose:
            print '>>>>>>>>>>> PROGRESS:', job_ind+1, '/', len(args_kwargs), 'done'
        ret[arg_ind] = result
    p.close()
    return ret
