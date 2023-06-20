from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext

from create_bot import bot
from keyboards import keyboards
from utils.databases import mysql_bd as db
from models import User


async def send_register(message: types.Message):
    mes_str = f"Войдите или зарегестрируйтесь"
    await message.answer(mes_str, reply_markup=keyboards.registration)


async def register(callback: types.CallbackQuery):
    await callback.message.answer(f'Регистрация\n' +
                                  f'Введите логин:', reply_markup=keyboards.cancel)


def register_handlers(dp: Dispatcher):

    # Start
    dp.register_message_handler(send_register, commands=["enter"])
    dp.register_callback_query_handler(register, text='register')