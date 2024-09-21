# -*- coding: utf- 8 -*-
from aiogram import Dispatcher, F

from . import main_errors, main_start, main_missed
from .admin import admin_menu, admin_functions
from .user import user_menu
from utils.filters import IsAdmin


# Регистрация всех роутеров
def register_all_routers(dp: Dispatcher):
	# Подключение фильтров
	dp.message.filter(F.chat.type == "private")  # Работа бота только в личке - сообщения
	dp.callback_query.filter(F.message.chat.type == "private")  # Работа бота только в личке - колбэки

	admin_menu.router.message.filter(IsAdmin())  # Работа роутера только для админов
	admin_functions.router.message.filter(IsAdmin())  # Работа роутера только для админов

	# Подключение обязательных роутеров
	dp.include_router(main_errors.router)  # Роутер ошибки
	dp.include_router(main_start.router)  # Роутер основных команд

	# Подключение пользовательских роутеров (юзеров и админов)
	dp.include_router(user_menu.router)  # Юзер роутер
	dp.include_router(admin_menu.router)  # Админ роутер
	dp.include_router(admin_functions.router)  # Админ роутер

	# Подключение обязательных роутеров
	dp.include_router(main_missed.router)  # Роутер пропущенных апдейтов
