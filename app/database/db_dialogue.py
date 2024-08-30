# -*- coding: utf- 8 -*-
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class DialogueModel(BaseModel):
	id: int
	admin_user_id: int
	user_id: int
	show: bool
	created_at: int

# Работа с юзером
class Dialoguex:
	# Добавление записи
	@staticmethod
	async def add(admin_user_id: int, user_id: int, show: bool = True, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO dialogues'
			sql, params = sql_insert_format(sql, admin_user_id=admin_user_id, user_id=user_id, show=show, created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = DialogueModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(**kwargs) -> DialogueModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM dialogues'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = DialogueModel(**resp)
			return resp

	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> DialogueModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM dialogues'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetch(sql, *params)
			resp = [DialogueModel(**x) for x in resp]
			return resp

	# Редактирование записи
	@staticmethod
	async def update(id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE dialogues'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)

	@staticmethod
	async def delete(**kwargs):
		async with db.pool.acquire() as conn:
			sql = 'DELETE FROM dialogues'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.execute(sql, *params)