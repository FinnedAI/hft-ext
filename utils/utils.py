import sqlite3


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
            yield iterable[ndx : min(ndx + n, l)]


class Storage:
    def __init__(self):
        self.conn = sqlite3.connect("data/ticker_data.db")
        self.create_table()

    def create_table(self):
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS ticker_data (
                        ticker text,
                        price real
                    )"""
        )
        self.conn.commit()

    def save_data(self, ticker, price):
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO ticker_data (ticker, price)
                    VALUES (?,?)""",
            (ticker, price),
        )
        self.conn.commit()

    def retrieve_data(self, ticker):
        c = self.conn.cursor()
        c.execute(
            """SELECT price FROM ticker_data
                    WHERE ticker=?""",
            (ticker,),
        )
        return c.fetchall()
