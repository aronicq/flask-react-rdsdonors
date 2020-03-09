import datetime
from operator import itemgetter

from flask import render_template


def load_page(conn):
    curs = conn.cursor()
    curs.execute("SELECT * FROM main.payments")

    rows = curs.fetchall()
    print(rows[0][1])
    rows.sort(key=lambda x: datetime.datetime.strptime(x[1], ' %d.%m.%Y %H:%M:%S'), reverse=True)


    conn.close()
    return rows[:100]