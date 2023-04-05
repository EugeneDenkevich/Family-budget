from decimal import Decimal
import mysql.connector as sq
from itertools import chain
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


def start_db():
    connect_db()
    create_tables()


def connect_db():
    global db, cur

    db = sq.connect(
        host="localhost",
        user=os.getenv('DB_USER'),
        passwd=os.getenv('DB_PASS'),
        port="3306"
    )

    cur = db.cursor()


def create_tables():
    cur.execute("CREATE DATABASE IF NOT EXISTS family_budget;")
    db.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.overal_balance (\
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2),\
                    fin_date VARCHAR(20),\
                    days VARCHAR(30)\
                    ) ENGINE = InnoDB;")

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.daily_balance (\
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2)\
                    ) ENGINE = InnoDB;")

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.today_balance (\
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2)\
                    ) ENGINE = InnoDB;")
    db.commit()


# Getters for balances ------------

async def get_overal():
    connect_db()
    cur.execute("SELECT summ, days FROM family_budget.overal_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.overal_balance);")
    res = cur.fetchall()
    return res[0][0], res[0][1]


async def get_daily():
    connect_db()
    cur.execute("SELECT summ FROM family_budget.daily_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.daily_balance);")
    res = cur.fetchall()
    return str(*chain(*res))


async def get_today():
    connect_db()
    cur.execute("SELECT summ FROM family_budget.today_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.today_balance);")
    res = cur.fetchall()
    return str(*chain(*res))


async def get_fin_date():
    connect_db()
    cur.execute("SELECT fin_date FROM family_budget.overal_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.overal_balance);")
    res = cur.fetchall()
    return str(*chain(*res))


# Setters for balances ------------

async def set_overal(summ, sum_date: str):
    connect_db()
    time_list = sum_date.split('.')
    start_date = datetime.now()
    finish_date = datetime(int(time_list[2]), int(
        time_list[1]), int(time_list[0]))
    delta = finish_date - start_date
    days = delta.days + 2
    finish_date = finish_date.strftime("%d.%m.%Y")
    await set_daily(summ, days)
    summ = Decimal(summ) - Decimal(await get_daily())
    cur.execute(
        f"INSERT INTO family_budget.overal_balance (summ, fin_date, days) VALUES ('{summ}', '{finish_date}', '{days}');")
    db.commit()


async def set_daily(summ, days):
    connect_db()

    summ = Decimal(summ)
    days = int(days)
    summ = round(summ / days)

    cur.execute(
        "INSERT INTO family_budget.daily_balance (summ) VALUES (%s)", [summ])
    db.commit()

    await set_today(summ)


async def set_today(summ):
    connect_db()
    cur.execute(
        "INSERT INTO family_budget.today_balance (summ) VALUES (%s)", [summ])
    db.commit()


async def set_overal_scheduler(summ):
    connect_db()
    summ = summ - Decimal((await get_daily()))
    cur.execute(f"UPDATE family_budget.overal_balance SET summ={summ}" +
                "WHERE id = (SELECT MAX(id)" +
                "FROM (SELECT * FROM family_budget.overal_balance) as timetalbe);")
    db.commit()
