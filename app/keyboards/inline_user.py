# -*- coding: utf- 8 -*-
from typing import Union

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import *
from utils.functions import *
from data.config import *


################################################################################
#################################### ПРОЧЕЕ ####################################
# Кнопка "Назад"
def kb_back(data: str = 'user:menu', text: str = '↪ Назад') -> InlineKeyboardMarkup:
	keyboard = ikb_construct(back_button=ikb(text, data=data))
	return keyboard.as_markup()

# Кнопка "Закрыть"
def kb_close(text: str = '❌ Закрыть') -> InlineKeyboardMarkup:
	keyboard = ikb_construct(back_button=ikb(text, data='utils:delete'))
	return keyboard.as_markup()




def kb_order_choose():
	keyboard = ikb_construct(
		[ikb('⚙️ Программирование', data='req:order:chs:programming'), ikb('🖌 Дизайн', data='req:order:chs:design')],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	return keyboard.as_markup()

def kb_application_choose():
	keyboard = ikb_construct(
		[ikb('⚙️ Кодер', data='req:application:chs:coder'), ikb('🖌 Дизайнер', data='req:application:chs:designer')],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	return keyboard.as_markup()


def kb_multi_state(req_type: str, req_sub_type: str, questions: dict, question_key: str, question_data: dict):
	if not question_key:
		keyboard = ikb_construct(
			[ikb('Да', data='True'), ikb('Нет', data='False')],
			back_button=ikb('↪ Назад', data='back')
		)
		return keyboard.as_markup()
	elif question_data.get('bool', False):
		keyboard = ikb_construct(
			*[[ikb(z, data=x[z]) for z in x] for x in question_data.get('inline_kb', {})],
			back_button=ikb('↪ Назад', data='back')
		)
		return keyboard.as_markup()
	elif len(question_data.get('reply_kb', [])) > 0 or (len(question_data.get('reply_kb', [])) > 0 and question_data.get('is_file', False)):
		keyboard = rkb_construct(
			*[[rkb(z) for z in x] for x in question_data.get('reply_kb', [])],
			[rkb('➡️ Пропустить')] if question_data.get('skipable', False) else [],
			[rkb('↪ Назад')]
		)
		return keyboard.as_markup(resize_keyboard=True)
	elif len(question_data.get('inline_kb', [])) > 0 or (len(question_data.get('inline_kb', [])) > 0 and question_data.get('is_file', False)):
		keyboard = ikb_construct(
			*[[ikb(z, data=x[z]) for z in x] for x in question_data.get('inline_kb', {})],
			[ikb('➡️ Пропустить', data='skip')] if question_data.get('skipable', False) else [],
			[ikb('↪ Назад', data='back')]
		)
		return keyboard.as_markup()
	elif question_data.get('skipable', False):
		keyboard = ikb_construct(
			[ikb('➡️ Пропустить', data='skip')],
			back_button=ikb('↪ Назад', data='back')
		)
		return keyboard.as_markup()
	else:
		keyboard = ikb_construct(
			[ikb('↪ Назад', data='back')]
		)
		return keyboard.as_markup()



# Информация
def kb_info() -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('📍 Администратор', url=url_administrator), ikb('🖼 Портфолио', url=url_portfolio)],
		[ikb('📝 Пользовательское соглашение', url=url_rules)], 
		[ikb('📜 Как оформить техническое задание?', url=url_tz)],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	return keyboard.as_markup()
################################################################################
################################### ПЛАТЕЖИ ####################################