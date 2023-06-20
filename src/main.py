from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import traceback
import datetime

from utils import logging
from utils.set_bot_commands import set_all_default_commands
from handlers import balance_handlers, \
    registration_handlers, \
    after_everything_handlers
from create_bot import dp, bot
from utils.databases import mysql_bd as db


async def start_bot(_):
    print("\n========================")
    print(
        f"--- Bot has started at {datetime.datetime.now().strftime('%H:%M, %d.%m.%Y')} ---")
    try:
        db.start_db()
        print("--- DB has connected ---")
        print("========================\n")
    except Exception:
        print("--- DB has not connected ---", traceback.format_exc())
        print("========================\n")

    await set_all_default_commands(bot)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # scheduler.add_job(balance_handlers.daily_balance_update, trigger='cron', hour='6',
    #                   minute='30', kwargs={'bot': bot})
    scheduler.add_job(balance_handlers.daily_balance_update, trigger='cron', hour=datetime.datetime.now().hour,
                      minute=datetime.datetime.now().minute + 1, kwargs={'bot': bot})
    scheduler.start()


if __name__ == "__main__":
    balance_handlers.register_handlers(dp)
    registration_handlers.register_handlers(dp)
    after_everything_handlers.register_handlers(dp)
    executor.start_polling(
        dispatcher=dp, skip_updates=True, on_startup=start_bot)
