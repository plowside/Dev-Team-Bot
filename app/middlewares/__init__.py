# -*- coding: utf- 8 -*-
from aiogram import Bot, Dispatcher

from .middleware_throttling import ThrottlingMiddleware
from .middleware_users import ExistsUserMiddleware


# Регистрация всех мидлварей
def register_all_middlwares(dp: Dispatcher, bot: Bot):
	dp.callback_query.outer_middleware(ExistsUserMiddleware(bot))
	dp.message.outer_middleware(ExistsUserMiddleware(bot))

	dp.message.middleware(ThrottlingMiddleware())