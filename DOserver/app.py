import datetime

import flask
import rds.mailChecker
import rds.load_datapage
from flask import Flask, g, request
from dateutil import relativedelta
import sqlite3

import flask_excel
from flask.json import jsonify
from flask_cors import CORS

app = Flask(__name__)
flask_excel.init_excel(app)
CORS(app)


@app.route('/download', methods=['GET'])
def download():
    from_date = datetime.datetime.strptime(request.args.get('from'), '%d%m%Y')
    to_date = datetime.datetime.strptime(request.args.get('to'), '%d%m%Y')
    conn = create_connection("dbfiles/db_file.db")
    curs = conn.cursor()

    curs.execute("SELECT * FROM main.payments")#3 город,
    rows = [i for i in curs.fetchall() #if i[3] != "Санкт-Петербург"
            if from_date < datetime.datetime.strptime(i[1], " %d.%m.%Y %H:%M:%S") < to_date]

    print(str(from_date) + str(to_date))
    print((str(from_date) + "<" + str(datetime.datetime.strptime(i[1], " %d.%m.%Y %H:%M:%S")) + "<" + str(to_date))
          for i in curs.fetchall()  # if i[3] != "Санкт-Петербург"
     if from_date < datetime.datetime.strptime(i[1], " %d.%m.%Y %H:%M:%S") < to_date)

    output = flask_excel.make_response_from_array(rows, "csv")
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def setting_up_db():
    """ creating connection to dbfile, tables.
    Checking correctness
    :return: Result message and connection object or None
    """
    result = "ok"
    sql_create_payments_table = """ CREATE TABLE IF NOT EXISTS payments (
                                    id integer PRIMARY KEY,
                                    time_date text NOT NULL,
                                    email text,
                                    city text,
                                    amount integer
                                );"""
    sql_create_daily_payments_table = """ CREATE TABLE IF NOT EXISTS dailypayments (
                                        id integer PRIMARY KEY,
                                        time_date text NOT NULL, 
                                        times_that_day integer,
                                        amount integer
                                    );"""
    conn = None

    try:
        conn = create_connection("dbfiles/db_file.db")
    except:
        result = "error! cannot create db connection"
        print(result)

    if conn is not None:
        create_table(conn, sql_create_payments_table)
        create_table(conn, sql_create_daily_payments_table)
    else:
        result = "Error! cannot create tables"
        print(result)

    return result, conn


@app.route("/react")
def reacted():
    return flask.render_template("index.html", token="flask + react")


@app.route("/")
def hello():
    result = "zdravstvuyte"
    return result


@app.route("/checkMail")
def mail():
    result, conn = setting_up_db()
    rds.mailChecker.regular_check(conn)
    return result


@app.route("/donations")
def showDonations():
    return flask.render_template("index.html")


@app.route("/api/getList")
def getListOfDonations():
    result, conn = setting_up_db()
    curs = conn.cursor()

    temp = rds.load_datapage.load_page(curs)
    return jsonify({"items": temp[0],
                    "donations_per_day": temp[1]})


@app.route("/daysLeft")
def days():
    date = datetime.date(2020, 9, 24)

    diff = relativedelta.relativedelta(datetime.datetime.strptime(str('2020-09-24'), '%Y-%m-%d'),
                                       datetime.date.today())

    full_sentence = relativedelta.relativedelta(datetime.datetime.strptime(str('2020-09-24'), '%Y-%m-%d'),
                                                datetime.datetime.strptime(str('2018-12-24'), '%Y-%m-%d'))

    return "days: " + str(abs((date.today() - date).days)) + "(" + str(abs((date.today() - date).days) - 32) + ")" + " \\ " + str(
        abs((datetime.date(2018, 12, 24) - date).days)) + "</br>" \
           + "weeks: " + str(abs(date.today() - date).days // 7) + "(" + str((abs((date.today() - date).days) - 32) // 7) + ")" + " \\ " + str(
        abs((datetime.date(2018, 12, 24) - date).days) // 7) + "</br>" \
           + "months: " + str(diff.years * 12 + diff.months + round(diff.days / 30, 1)) + "(" + str(diff.years * 12 + diff.months + round((diff.days  - 32) / 30, 1)) + ")" + " \\ " + str(
        full_sentence.years * 12 + full_sentence.months + round(full_sentence.days / 30, 1))


if __name__ == "__main__":
    flask_excel.init_excel(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
