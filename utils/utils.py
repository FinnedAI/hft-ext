class Utils:
    @staticmethod
    def batch(iterable, n):
        """
        Yield iterable in batches of n. If iterable is less than n, return iterable.

        :param iterable: The iterable to be processed
        :type iterable: list, tuple, or any other iterable
        :param n: The batch size
        :type n: int
        :return: Yields iterable in batches of size n
        :rtype: generator
        """
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
