import multiprocessing as mp

def wrapper_fcn((fn, (i, args_kwargs))):
    return i, fn(*args_kwargs[0], **args_kwargs[1])

def pmap(fn, args_kwargs, verbose=True, super_verbose=False):
    """ Multiprocessing abstraction that includes a progress meter.
        Usage:
            def foo(x): return x * 2
            pmap(foo, [([1], {}), ([2], {})]) => [2, 4]

    """
    try:
        p = mp.Pool(mp.cpu_count())
        ret = [None] * len(args_kwargs)

        processed_args = [(fn, (i, a_k)) for i, a_k in enumerate(args_kwargs)]

        for job_ind, (arg_ind, result) in \
                enumerate(p.imap_unordered(wrapper_fcn, processed_args, chunksize=1)):
            if verbose:
                print '>>>>>>>>>>> PROGRESS:', job_ind+1, '/', len(args_kwargs), 'done'
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
                print '>>>>>>>>>>> PROGRESS:', i+1, '/', len(args_kwargs), 'done'
            ret.append(fn(*args, **kwargs))

        # Throw the original if we didn't hit any exception in the single-threaded execution
        raise
        return ret
