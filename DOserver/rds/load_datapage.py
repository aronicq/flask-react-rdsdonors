import datetime


def load_page(curs):
    curs.execute("SELECT * FROM main.payments")
    rows = curs.fetchall()

    rows.sort(key=lambda x: datetime.datetime.strptime(x[1], ' %d.%m.%Y %H:%M:%S'), reverse=True)
    rows = [(a, *b.strip().split(" "), c, d, e) for (a, b, c, d, e) in rows]


    curs.execute("SELECT * FROM main.dailypayments")
    dailyrows = {str(x).strip().split(" ")[0]: {"donations_per_day": y, "sum_that_day": z} for (index, x, y, z) in curs.fetchall()}
    #

    print(dailyrows)
    return rows, dailyrows