import collections

def dd_to_d(dd):
    return dict((k, dd_to_d(v) if isinstance(v, collections.defaultdict) else v)
            for k, v in dd.iteritems())

def dd(constructor, nlevels=1):
    if nlevels == 1:
        c = constructor
    else:
        c = lambda: dd(constructor, nlevels-1)
    return collections.defaultdict(c)

def ig(*idxs):
    def w(nested):
        ret = nested
        for i in idxs:
            ret = ret[i]
        return ret
    return w
