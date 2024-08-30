from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from data.config import telegram_token

dp = Dispatcher()
bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode='HTML'))
custom_fsm = {'dialogue': {}}