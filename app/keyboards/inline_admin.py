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
def kb_back(data: str = 'admin:menu', text: str = '↪ Назад') -> InlineKeyboardMarkup:
	keyboard = ikb_construct(back_button=ikb(text, data=data))
	return keyboard.as_markup()

# Кнопка "Закрыть"
def kb_close(text: str = '❌ Закрыть') -> InlineKeyboardMarkup:
	keyboard = ikb_construct(back_button=ikb(text, data='utils:delete'))
	return keyboard.as_markup()



# Меню админа
def kb_admin_menu() -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('Найти пользователя', data='admin:search'), ikb('Все запросы', data='admin:requests')],
		back_button=ikb('❌ Закрыть', data='utils:delete')
	)
	return keyboard.as_markup()


# Поиск пользователя
def kb_admin_search() -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		back_button=ikb('↪ Назад', data='admin:menu')
	)
	return keyboard.as_markup()

# Меню найденного пользователя
def kb_admin_user(user_id: int) -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('Диалог', data=f'admin:dialogue:menu:{user_id}'), ikb('Запросы', data=f'admin:requests:0:0:0:{user_id}')],
		back_button=ikb('↪ Назад', data='admin:menu')
	)
	return keyboard.as_markup()

def kb_admin_user_dialogue(user_id: int, dialogue_id: int = None) -> InlineKeyboardMarkup:
	btns = [
		[ikb('➡️ Продолжить существующий', data=f'admin:dialogue:continue:{user_id}:{dialogue_id}')],
		[ikb('📄 Начать новый', data=f'admin:dialogue:start:{user_id}')]
	] if dialogue_id else [[ikb('📄 Начать новый', data=f'admin:dialogue:start:{user_id}')]]
	keyboard = ikb_construct(
		*btns,
		back_button=ikb('↪ Назад', data=f'admin:search:{user_id}')
	)
	return keyboard.as_markup()


def kb_admin_request(req_id: int, req_table: str, req_user_id: int, req_status: int = 0, req_type: int = 0, page: int = 0, user_id: int = None):
	keyboard = ikb_construct(
		[ikb('Найти пользователя', data=f'admin:search:{req_user_id}'), ikb('Завершить запрос', data=f'admin:request:c:{req_id}:{req_table}:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')],
		back_button=ikb('↪ Назад', data=f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')
	)
	return keyboard.as_markup()

# Меню найденных запросов
def kb_admin_requests(requests: list, req_status: int = 0, req_type: int = 0, page: list = (False, 0, True), user_id: int = None) -> InlineKeyboardMarkup:
	trns = {'q': {'designer': 'Дизайнер', 'coder': 'Кодер', 'order': 'Заказ'}, 'type': {0: '⚪️ Все', 1: 'Заказы', 2: 'Кодеры', 3: 'Дизайнеры'}, 'status': {0: '⚪️ Все', 1: '🟢 Активные', 2: '🔴 Завершенные'}}
	s = [[ikb(f'{trns["q"][x["q"]]} | {x["id"]} | {x["user_id"]}', data=f'admin:request:s:{x["id"]}:{x["q"]}:{req_status}:{req_type}:{page[1]}{":"+str(user_id) if user_id else ""}')] for x in requests]
	pag_btns = []
	if page[0]: pag_btns.append(ikb('❮❮', data=f'admin:requests:{req_status}:{req_type}:{page[1] - 1}{":"+str(user_id) if user_id else ""}'))
	if page[2]: pag_btns.append(ikb('❯❯', data=f'admin:requests:{req_status}:{req_type}:{page[1] + 1}{":"+str(user_id) if user_id else ""}'))
	keyboard = ikb_construct(
		*s,
		[ikb(f"Статус: {trns['status'][req_status]}", data=f'admin:requests:{req_status + 1 if req_status <= 1 else 0}:{req_type}:{page[1]}{":"+str(user_id) if user_id else ""}'), ikb(f"Тип: {trns['type'][req_type]}", data=f'admin:requests:{req_status}:{req_type + 1 if req_type <= 2 else 0}:{page[1]}{":"+str(user_id) if user_id else ""}')],
		pag_btns,
		back_button=ikb('↪ Назад', data='admin:menu')
	)
	return keyboard.as_markup()