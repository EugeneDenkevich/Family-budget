from aiogram import types, Dispatcher, Bot
from create_bot import bot
import keyboards
import mysql_bd as db
from models import User
from aiogram.dispatcher import FSMContext


async def send_register(message: types.Message):
    mes_str = f"Войдите или зарегестрируйтесь"
    await message.answer(mes_str, reply_markup=keyboards.registration)


def register_handlers(dp: Dispatcher):

    # Start
    dp.register_message_handler(send_register, commands=["enter"])