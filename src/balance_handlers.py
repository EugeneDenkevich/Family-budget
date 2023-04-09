from aiogram import types, Dispatcher, Bot
from create_bot import bot
from keyboards import start, choose_change, cancel
import mysql_bd as db
from models import Balance, Buy
from aiogram.dispatcher import FSMContext
from decimal import Decimal
from aiogram_calendar.simple_calendar import calendar_callback, SimpleCalendar
import requests
from bs4 import BeautifulSoup


def get_fuel():
    res = requests.get(
        url=f'https://azs.a-100.by/set-azs/fuel/')
    soup = BeautifulSoup(res.text, 'lxml')
    quotes = soup.find_all('div', class_='price')
    price = ''
    for i in quotes[1].text:
        if i == '\n':
            continue
        price += i
    price = price[0] + '.' + price[1:3]
    return price


def get_dollar():
    res = requests.get(url='https://myfin.by/currency/usd')
    soup = BeautifulSoup(res.text, 'lxml')
    quotes = soup.find('div', class_='c-best-rates').find('tbody').contents
    price_sell = quotes[0].contents[1].text
    price_buy = quotes[0].contents[2].text
    return price_sell, price_buy


# Start

async def send_start(message: types.Message):
    s1 = str((await db.get_overal())[0])
    s2 = await db.get_daily()
    s3 = await db.get_today()
    d1 = await db.get_fin_date()
    mes_str = f"Остаток: {s1} BYN по {d1}\nБаланс суточный: {s2} BYN\n" + \
              f"Остаток на сегодня: {s3} BYN\n" + \
              f"Курс доллара: {get_dollar()[0]} Br, {get_dollar()[1]} Br\n" + \
              f"Стоимость 95 бензина: {get_fuel()} Br"
    await message.answer(mes_str, reply_markup=start)


# Balance overal

async def change_overal(callback: types.CallbackQuery):
    await Balance.date.set()
    await callback.message.answer('По какое число?', reply_markup=await SimpleCalendar().start_calendar())


async def process_calendar(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        async with state.proxy() as data:
            data['date'] = date.strftime("%d.%m.%Y")
        await Balance.overal.set()
        await callback.message.answer('Введите сумму:', reply_markup=cancel)


async def set_overal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await db.set_overal(message.text, data['date'])
    await state.finish()
    await send_start(message)


async def change_daily(callback: types.CallbackQuery):
    await Balance.daily.set()
    await callback.message.answer('Сумма:', reply_markup=cancel)


async def set_daily(message: types.Message, state: FSMContext):
    await db.set_daily(message.text)
    await state.finish()
    await send_start(message)


# Balance for today

async def buy(callback: types.CallbackQuery):
    await Buy.buy.set()
    await callback.message.answer('Сумма:', reply_markup=cancel)


async def set_today(message: types.Message, state: FSMContext):
    res = Decimal(await db.get_today()) - Decimal(message.text)
    await db.set_today(str(res))
    await state.finish()
    await send_start(message)


# Scheduled functions

async def daily_balance_update(bot: Bot):
    overal = (await db.get_overal())[0]
    daily = Decimal(await db.get_daily())
    today = Decimal(await db.get_today())
    overal = overal - daily
    today = today + daily
    d1 = await db.get_fin_date()
    await db.set_overal_scheduler(overal)
    await db.set_today(today)
    mes_str = f"Обновление баланса прошло успешно.\n" \
              f"Остаток: {overal} BYN по {d1}\nБаланс суточный: {daily} BYN\n" + \
              f"Остаток на сегодня: {today} BYN\n" + \
              f"Курс доллара: {get_dollar()[0]} Br, {get_dollar()[1]} Br\n" + \
              f"Стоимость 95 бензина: {get_fuel()} Br"
    await bot.send_message(chat_id=5508567586, text=mes_str, reply_markup=start)


# Cancel/Back

async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    s1 = str((await db.get_overal())[0])
    s2 = await db.get_daily()
    s3 = await db.get_today()
    d1 = await db.get_fin_date()
    mes_str = f"Остаток: {s1} BYN по {d1}\nБаланс суточный: {s2} BYN\n" + \
              f"Остаток на сегодня: {s3} BYN\n" + \
              f"Курс доллара: {get_dollar()[0]} Br, {get_dollar()[1]} Br\n" + \
              f"Стоимость 95 бензина: {get_fuel()} Br"
    await callback.message.answer(mes_str, reply_markup=start)


def register_handlers(dp: Dispatcher):

    # Start
    dp.register_message_handler(send_start, commands=["start"])

    # Overal
    dp.register_callback_query_handler(change_overal, text="change")
    dp.register_callback_query_handler(
        process_calendar, calendar_callback.filter(), state=Balance.date)
    dp.register_message_handler(set_overal, state=Balance.overal)

    dp.register_callback_query_handler(change_daily, text="change_daily")
    dp.register_callback_query_handler(buy, text="purchase")
    dp.register_message_handler(set_daily, state=Balance.daily)
    dp.register_message_handler(set_today, state=Buy.buy)
    dp.register_callback_query_handler(go_back, text="back")
    dp.register_callback_query_handler(go_back, text='cancel', state='*')
