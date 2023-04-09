from create_bot import dp
from aiogram.utils import executor
import balance_handlers
import registration_handlers
from mysql_bd import start_db
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import balance_handlers
from datetime import datetime
from create_bot import bot


async def start_bot(_):
    print("--- Bot has starterd ---")
    try:
        start_db()
        print("--- DB has connected ---")
    except Exception:
        print("--- DB has not connected ---", traceback.format_exc())
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    print(datetime.now())
    scheduler.add_job(balance_handlers.daily_balance_update, trigger='cron', hour='6',
                      minute='30', kwargs={'bot': bot})
    scheduler.start()

if __name__ == "__main__":
    balance_handlers.register_handlers(dp)
    registration_handlers.register_handlers(dp)
    executor.start_polling(
        dispatcher=dp, skip_updates=True, on_startup=start_bot)
