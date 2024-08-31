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
def kb_admin_menu(admin_tg_user_id: int) -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('🔍 Найти пользователя', data='admin:search'), ikb('Все запросы', data='admin:requests')] if admin_tg_user_id in admin_ids else [ikb('🔍 Найти пользователя', data='admin:search')],
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
def kb_admin_user(admin_tg_user_id: int, user_id: int) -> InlineKeyboardMarkup:
	keyboard = ikb_construct(
		[ikb('Диалог', data=f'admin:dialogue:menu:{user_id}'), ikb('Запросы', data=f'admin:requests:0:0:0:{user_id}')] if admin_tg_user_id in admin_ids else [ikb('Диалог', data=f'admin:dialogue:menu:{user_id}')],
		back_button=ikb('↪ Назад', data='admin:menu')
	)
	return keyboard.as_markup()


# Меню диалога
def kb_admin_user_dialogue(admin_tg_user_id: int, user_id: int, dialogue_id: int = None) -> InlineKeyboardMarkup:
	btns = [
		[ikb('Продолжить существующий ➡️', data=f'admin:dialogue:continue:{user_id}:{dialogue_id}'), ikb('📄 Начать новый', data=f'admin:dialogue:start:{user_id}')] if dialogue_id else [ikb('📄 Начать новый', data=f'admin:dialogue:start:{user_id}')]
	] 
	if admin_tg_user_id in admin_ids: btns.append([ikb('🗄 История диалогов', data=f'admin:dialogue:history:{user_id}')])
	keyboard = ikb_construct(
		*btns,
		back_button=ikb('↪ Назад', data=f'admin:search:{user_id}')
	)
	return keyboard.as_markup()

# История диалогов
def kb_admin_user_dialogues(user_id: int, dialogues: list) -> InlineKeyboardMarkup:
	btns = [[ikb(f'{trns_all.get("indicators", {}).get("emoji2", {}).get(dialogue.show, "⚪️")} {dialogue.id} | {dialogue.admin_user_id}', data=f'admin:dialogue:show:{user_id}:{dialogue.id}') for dialogue in dialogues]]
	btns.append([ikb('🗑 Очистить историю', data=f'admin:dialogue:clear_history:{user_id}')])
	keyboard = ikb_construct(
		*btns,
		back_button=ikb('↪ Назад', data=f'admin:dialogue:menu:{user_id}')
	)
	return keyboard.as_markup()


# Меню найденных запросов
def kb_admin_requests(requests: list, req_status: int = 0, req_type: int = 0, page: list = (False, 0, True), user_id: int = None) -> InlineKeyboardMarkup:
	trns = trns_all.get('kb_admin_requests', {})
	s = [[ikb(f'{trns.get("q", {}).get(x.req_type, {}).get(x.req_sub_type, None)} | {x.uuid}', data=f'admin:request:s:{x.id}:{req_status}:{req_type}:{page[1]}{":"+str(user_id) if user_id else ""}')] for x in requests]
	pag_btns = []
	if page[0]: pag_btns.append(ikb('❮❮', data=f'admin:requests:{req_status}:{req_type}:{page[1] - 1}{":"+str(user_id) if user_id else ""}'))
	if page[2]: pag_btns.append(ikb('❯❯', data=f'admin:requests:{req_status}:{req_type}:{page[1] + 1}{":"+str(user_id) if user_id else ""}'))
	keyboard = ikb_construct(
		*s,
		[ikb(f"Статус: {trns['status'][req_status]}", data=f'admin:requests:{req_status + 1 if req_status <= 1 else 0}:{req_type}:{page[1]}{":"+str(user_id) if user_id else ""}'), ikb(f"Тип: {trns['type'][req_type]}", data=f'admin:requests:{req_status}:{req_type + 1 if req_type <= 1 else 0}:{page[1]}{":"+str(user_id) if user_id else ""}')],
		[ikb('Найти запрос', data=f'admin:request_search:{req_status}:{req_type}:{page[1]}{":"+str(user_id) if user_id else ""}')],
		pag_btns,
		back_button=ikb('↪ Назад', data='admin:menu')
	)
	return keyboard.as_markup()

# Управление запросом
def kb_admin_request(admin_tg_user_id: int, req: Requestx.model, req_files: list, req_status: int = 0, req_type: int = 0, page: int = 0, user_id: int = None):
	if len(req_files) > 0:
		btns = [
			[ikb('🗂 Получить файлы', data=f'admin:request:gf:{req.id}:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')],
			[ikb('🔍 Найти пользователя', data=f'admin:search:{req.user_id}')]
		]
	else:
		btns = [
			[ikb('🔍 Найти пользователя', data=f'admin:search:{req.user_id}')]
		]
	if not req.completed: btns.append([ikb('Завершить запрос', data=f'admin:request:c:{req.id}:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')])
	if admin_tg_user_id in admin_ids: btns.append([ikb('🗑 Удалить запрос', data=f'admin:request:d:{req.id}:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')])
	keyboard = ikb_construct(
		*btns,
		back_button=ikb('↪ Назад', data=f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')
	)
	return keyboard.as_markup()
