import datetime
from operator import itemgetter
from flask import render_template


def load_page(curs):
    # curs = conn.cursor()
    curs.execute("SELECT * FROM main.payments")
    rows = curs.fetchall()

    rows.sort(key=lambda x: datetime.datetime.strptime(x[1], ' %d.%m.%Y %H:%M:%S'), reverse=True)

    conn.close()
    return rows