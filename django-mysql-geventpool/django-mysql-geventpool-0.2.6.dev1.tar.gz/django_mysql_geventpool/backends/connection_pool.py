import logging
try:
    from gevent import queue
except ImportError:
    from eventlet import queue

logger = logging.getLogger('django.geventpool')


class DatabaseConnectionPool:
    def __init__(self, maxsize=100, maxlifetime=0):
        self.maxsize = maxsize
        self.maxlifetime = maxlifetime
        self.pool = queue.Queue(maxsize=maxsize)
        self.size = 0

    def get(self, conn_params):
        conn = self._get_usable_connection()
        if conn:
            return conn
        if self.size >= self.maxsize or self.pool.qsize():
            conn = self.pool.get()
            if not self.is_usable(conn):
                try:
                    conn.close()
                except Exception:
                    pass
                conn = self.create_connection(conn_params)
            return conn
        else:
            self.size += 1
            try:
                conn = self.create_connection(conn_params)
            except Exception:
                self.size -= 1
                raise
            return conn

    def _get_usable_connection(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            if self.is_usable(conn):
                return conn
            else:
                try:
                    conn.close()
                except Exception:
                    pass
                self.put(None)
        return None

    def put(self, item):
        if item is None:
            self.size -= 1
            return
        try:
            self.pool.put(item, timeout=2)
        except queue.Full:
            item.close()

    def closeall(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except Exception:
                pass
        self.size = 0

    def create_connection(self, *args, **kwargs):
        raise NotImplementedError("create_connection")

    def is_usable(self, obj):
        raise NotImplementedError("is_usable")
