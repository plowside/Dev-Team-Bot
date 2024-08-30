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



def kb_choose_profession():
	keyboard = ikb_construct(
		[ikb('Кодер', data='user:req:coder'), ikb('Дизайнер', data='user:req:designer')],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	return keyboard.as_markup()


# Создание заказа
def kb_create_order(state: str) -> InlineKeyboardMarkup:
	if state in ['start', 'point_of_work', 'deadline', 'budget']:
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'create':
		keyboard = ikb_construct(
			[ikb('Создать заказ', data=f'missed:cod:y'), ikb('Отмена', data=f'missed:cod:n')],
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'created':
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:main')
		)

	return keyboard.as_markup()


# Создание заявки на кодера
def kb_create_coder(state: str) -> InlineKeyboardMarkup:
	if state in ['start', 'age', 'stack', 'portfolio', 'extra_information']:
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'complete_test_task':
		keyboard = ikb_construct(
			[ikb('Да', data='missed:acd:y'), ikb('Нет', data='missed:acd:n')],
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'create':
		keyboard = ikb_construct(
			[ikb('Создать заявку', data=f'missed:cod:y'), ikb('Отмена', data=f'missed:cod:n')],
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'created':
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:main')
		)

	return keyboard.as_markup()

# Создание заявки на дизайнера
def kb_create_designer(state: str) -> InlineKeyboardMarkup:
	if state in ['start', 'age', 'stack', 'services_provided', 'extra_information']:
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'create':
		keyboard = ikb_construct(
			[ikb('Создать заявку', data=f'missed:cod:y'), ikb('Отмена', data=f'missed:cod:n')],
			back_button=ikb('↪ Назад', data=f'missed:cst:{state}')
		)
	elif state == 'created':
		keyboard = ikb_construct(
			back_button=ikb('↪ Назад', data=f'utils:menu:main')
		)

	return keyboard.as_markup()


# Информация
def kb_info() -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('👤 Администратор', url=url_administrator), ikb('📝 Портфолио', url=url_portfolio)],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	
	return keyboard.as_markup()
################################################################################
################################### ПЛАТЕЖИ ####################################