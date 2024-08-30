# -*- coding: utf- 8 -*-
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class DialogueMessageModel(BaseModel):
	id: int
	dialogue_id: int
	message_id: int
	message_content_type: str
	message_text: str | None = None
	from_user_id: int
	from_user_tg_id: int
	from_user_type: str
	created_at: int

# Работа с юзером
class DialogueMessagex:
	# Добавление записи
	@staticmethod
	async def add(dialogue_id: int, message_id: int, message_content_type: str, message_text: str, from_user_id: int, from_user_tg_id: int, from_user_type: str, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO dialogue_messages'
			sql, params = sql_insert_format(sql, dialogue_id=dialogue_id, message_id=message_id, message_content_type=message_content_type, message_text=message_text, from_user_id=from_user_id, from_user_tg_id=from_user_tg_id, from_user_type=from_user_type, created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = DialogueMessageModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(**kwargs) -> DialogueMessageModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM dialogue_messages'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = DialogueMessageModel(**resp)
			return resp

	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> DialogueMessageModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM dialogue_messages'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetch(sql, *params)
			resp = [DialogueMessageModel(**x) for x in resp]
			return resp

	# Редактирование записи
	@staticmethod
	async def update(id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE dialogue_messages'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)