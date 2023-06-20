from aiogram import Bot, types



async def set_all_default_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand('start', 'Старт'),
        types.BotCommand('enter', 'Вход'),
    ])