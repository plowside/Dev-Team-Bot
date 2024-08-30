# -*- coding: utf-8 -*-
import asyncio, sys, os

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loader import dp, bot
from database import db
from middlewares import register_all_middlwares
from routers import register_all_routers
from utils.logging import logging

async def scheduler_start(bot: Bot):
	scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
	#scheduler.add_job(update_profit_month, trigger="cron", day=1, hour=00, minute=00, second=5)
	#scheduler.add_job(update_profit_week, trigger="cron", day_of_week="mon", hour=00, minute=00, second=10)
	#scheduler.add_job(update_profit_day, trigger="cron", hour=00, minute=00, second=15, args=(bot,))
	#scheduler.add_job(autobackup_admin, trigger="cron", hour=00, args=(bot,))
	#scheduler.add_job(check_update, trigger="cron", hour=00, args=(bot,))
	#scheduler.add_job(check_mail, trigger="cron", hour=12, args=(bot,))

async def main():
	await db.init_pool()

	register_all_middlwares(dp, bot)	# Регистрация всех мидлварей
	register_all_routers(dp)	# Регистрация всех роутеров

	try:
		await scheduler_start(bot)	# Подключение шедулеров

		await bot.delete_webhook()
		await bot.get_updates(offset=-1)

		logging.info('Bot was started')
		await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
	finally:
		await bot.session.close()


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as e:
		raise e