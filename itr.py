def ig(*idxs):
    def w(nested):
        ret = nested
        for i in idxs:
            ret = ret[i]
        return ret
    return w
