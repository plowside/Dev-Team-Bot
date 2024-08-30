# -*- coding: utf- 8 -*-
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils.functions import *
from data.config import admin_ids


# Кнопки главного меню
def kb_admin_dialogue() -> ReplyKeyboardMarkup:
	keyboard = rkb_construct(
		[rkb('📝 Сохранить диалог')],
		[rkb('❌ Завершить диалог')]
	)

	return keyboard.as_markup(resize_keyboard=True)