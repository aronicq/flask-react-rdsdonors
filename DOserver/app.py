import datetime

import flask
import rds.mailChecker
import rds.load_datapage
from flask import Flask
from dateutil import relativedelta
import sqlite3

app = Flask(__name__)


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


@app.route("/react")
def reacted():
    return flask.render_template("index.html", token="flask + react")


@app.route("/")
def hello():
    result = "zdravstvuyte"
    return result


@app.route("/blacklist")
def blacklist():
    return ""


@app.route("/checkMail")
def mail():
    sql_create_payments_table = """ CREATE TABLE IF NOT EXISTS payments (
                                    id integer PRIMARY KEY,
                                    time_date text NOT NULL, 
                                    email text,
                                    city text,
                                    amount integer
                                );"""
    conn = create_connection("db_file.db")
    if conn is not None:
        create_table(conn, sql_create_payments_table)
    else:
        result = "Error! cannot create the database connection."
        print(result)

    # rds.mailChecker.check(conn)
    return flask.render_template("index.html", rows=rds.load_datapage.load_page(conn))


@app.route("/daysLeft")
def days():
    date = datetime.date(2020, 9, 24)

    diff = relativedelta.relativedelta(datetime.datetime.strptime(str('2020-09-24'), '%Y-%m-%d'),
                                       datetime.date.today())

    full_sentence = relativedelta.relativedelta(datetime.datetime.strptime(str('2020-09-24'), '%Y-%m-%d'),
                                                datetime.datetime.strptime(str('2018-12-24'), '%Y-%m-%d'))

    return "days: " + str(abs((date.today() - date).days)) + " \\ " + str(
        abs((datetime.date(2018, 12, 24) - date).days)) + "</br>" \
           + "weeks: " + str(abs(date.today() - date).days // 7) + " \\ " + str(
        abs((datetime.date(2018, 12, 24) - date).days) // 7) + "</br>" \
           + "months: " + str(diff.years * 12 + diff.months + round(diff.days / 30, 1)) + " \\ " + str(
        full_sentence.years * 12 + full_sentence.months + round(full_sentence.days / 30, 1))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
