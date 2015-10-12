import multiprocessing as mp

def pmap(fn, args_kwargs):
    """ Multiprocessing abstraction that includes a progress meter.
        Usage:
            def foo(x): return x * 2
            pmap(foo, [([1], {}), ([2], {})]) => [2, 4]

    """
    p = mp.Pool(mp.cpu_count())
    ret = [None] * len(args_kwargs)

    for job_ind, (arg_ind, result) in \
            enumerate(p.imap_unordered(fn, list(enumerate(args_kwargs)), chunksize=1)):
        print '\n>>>>>>>>>>> PROGRESS:', job_ind+1, '/', len(args_kwargs), 'done\n'
        ret[arg_ind] = result
    p.close()
    return ret
