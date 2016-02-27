import collections

def _is_d(v):
    return isinstance(v, dict) or isinstance(v, collections.defaultdict)

def dd_to_d(dd):
    return dict((k, dd_to_d(v) if isinstance(v, collections.defaultdict) else v)
            for k, v in dd.iteritems())

def dd(constructor, nlevels=1):
    if nlevels == 1:
        c = constructor
    else:
        c = lambda: dd(constructor, nlevels-1)
    return collections.defaultdict(c)

def d_keys(d, level=0):
    assert level >= 0
    if level == 0:
        return d.keys()
    else:
        ret = set()
        for v in d.itervalues():
            ret |= set(d_keys(v, level-1))
        return ret

class _NoDefault(object): pass

def ig(*idxs, **kwargs):
    default = kwargs.get('default', _NoDefault)
    def w(nested):
        ret = nested
        for i in idxs:
            try:
                ret = ret[i]
            except:
                if default is _NoDefault:
                    raise
                else:
                    return default
        return ret
    return w

def iter_nested_d(d):
    for k, v in d.iteritems():
        if _is_d(v):
            for key_tup, value in iter_nested_d(v):
                yield (k,) + key_tup, value
        else:
            yield (k,), v
