def _bisect(is_below, xmin, xmax, eps, midpt):
    if is_below(xmax): return xmax
    if not is_below(xmin): return xmin

    def loop(xmin, xmax):
        # Find the midpoint of xmin and xmax |xmin-xmax|<=eps and
        # is_below(xmin)=True and is_below(xmax)=False
        assert is_below(xmin) and not is_below(xmax)
        mid = midpt(xmin, xmax)
        if abs(xmin - xmax) <= eps:
            return mid
        else:
            return loop(mid, xmax) if is_below(mid) else loop(xmin, mid)
    return loop(xmin, xmax)

def bisect_int(is_below, xmin, xmax):
    return _bisect(is_below, xmin, xmax, eps=1, midpt=lambda a, b: int((a+b)/2))

def bisect_float(is_below, xmin, xmax, eps=1e-3):
    return _bisect(is_below, xmin, xmax, eps=eps, midpt=lambda a, b: (a+b)/2.)


