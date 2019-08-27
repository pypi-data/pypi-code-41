import datetime
import sqlite3


def target_sqlite(metrics, **kwargs):
    path = kwargs.get('path', 'metric_results.db')
    table = kwargs.get('table', 'metrics')
    table = table.replace(',', '').replace(';', '')  # Really insecure security solution
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists {table}
                  (metric text, timestamp text, result text)'''.format(table=table))

    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    values = []
    for name, metric in metrics.items():
        values.append((name, timestamp, metric['result']))

    c.executemany('INSERT INTO {table} VALUES (?,?,?)'.format(table=table), values)

    conn.commit()
    conn.close()
