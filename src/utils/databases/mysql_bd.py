from decimal import Decimal
import mysql.connector as sq
from itertools import chain
from datetime import datetime

from data.config import DB_USER, DB_PASS


def start_db():
    connect_db()
    create_tables()


def connect_db():
    global db, cur

    db = sq.connect(
        host="localhost",
        user=DB_USER,
        passwd=DB_PASS,
        port="3306"
    )

    cur = db.cursor()


def create_tables():
    cur.execute("CREATE DATABASE IF NOT EXISTS family_budget;")
    db.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.users (\
                    id_user BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    login VARCHAR(255),\
                    password TEXT\
                    ) ENGINE = InnoDB;")

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.overal_balance (\
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2),\
                    fin_date VARCHAR(20),\
                    days VARCHAR(30),\
                    user_id BIGINT,\
                    FOREIGN KEY (user_id) REFERENCES users (id_user)\
                    ) ENGINE = InnoDB;")

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.daily_balance (\
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2),\
                    user_id BIGINT,\
                    FOREIGN KEY (user_id) REFERENCES users (id_user)\
                    ) ENGINE = InnoDB;")

    cur.execute("CREATE TABLE IF NOT EXISTS family_budget.today_balance (\
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                    summ DECIMAL(10,2),\
                    user_id BIGINT,\
                    FOREIGN KEY (user_id) REFERENCES users (id_user)\
                    ) ENGINE = InnoDB;")
    db.commit()


# Getters ------------

async def get_overal():
    connect_db()
    cur.execute("SELECT summ, days FROM family_budget.overal_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.overal_balance);")
    res = cur.fetchall()
    if res == []:
        return 0, 0
    return res[0][0], res[0][1]


async def get_daily():
    connect_db()
    cur.execute("SELECT summ FROM family_budget.daily_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.daily_balance);")
    res = cur.fetchall()
    if res == []:
        return 0
    return str(*chain(*res))


async def get_today():
    connect_db()
    cur.execute("SELECT summ FROM family_budget.today_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.today_balance);")
    res = cur.fetchall()
    if res == []:
        return 0
    return str(*chain(*res))


async def get_fin_date():
    connect_db()
    cur.execute("SELECT fin_date FROM family_budget.overal_balance WHERE id =\
                (SELECT MAX(id) FROM family_budget.overal_balance);")
    res = cur.fetchall()
    return str(*chain(*res))


# Setters ------------

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
    try:
        id = "SELECT MAX(id) FROM (SELECT * FROM family_budget.overal_balance) as timetalbe"
    except:
        return
    cur.execute(
        "UPDATE family_budget.overal_balance SET summ=%s WHERE id = (%s);", [summ, id])
    db.commit()
