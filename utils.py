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
        if len(iterable) < n:
            yield iterable
        else:
            for i in range(0, len(iterable), n):
                yield iterable[i : i + n]
