from aiogram import types, Dispatcher, Bot


# Any message
async def any_message(message: types.Message):
    """
    This handler handles any unneccessary message
    """
    await message.answer('Нажмите /start')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(any_message)
