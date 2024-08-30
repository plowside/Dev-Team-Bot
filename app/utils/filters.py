# -*- coding: utf- 8 -*-
from typing import Union

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from loader import custom_fsm
from data.config import admin_ids, moderator_ids

# Проверка на админа
class IsAdmin(BaseFilter):
	async def __call__(self, update: Union[Message, CallbackQuery], bot: Bot) -> bool:
		if update.from_user.id in [*admin_ids, *moderator_ids]:
			return True
		else:
			return False

class IsDialogue(BaseFilter):
	async def __call__(self, update: Union[Message, CallbackQuery], bot: Bot) -> bool:
		return update.from_user.id in custom_fsm['dialogue']
