class Utils:
    def batch(self, iterable, n):
        # if iterable is less than n, return iterable
        if len(iterable) < n:
            return iterable
        # else, return iterable in batches of n
        else:
            for i in range(0, len(iterable), n):
                yield iterable[i : i + n]
