# -*- coding: utf- 8 -*-
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class CoderModel(BaseModel):
	id: int
	user_id: int
	age: str
	stack: str
	portfolio: str
	extra_information: str
	complete_test_task: bool
	completed: bool
	created_at: int

# Работа с юзером
class Coderx:
	# Добавление записи
	@staticmethod
	async def add(user_id: int, age: str, stack: str, extra_information: str, complete_test_task: bool, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO coders'
			sql, params = sql_insert_format(sql, user_id=user_id, age=age, stack=stack, extra_information=extra_information, complete_test_task=complete_test_task, created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = CoderModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(**kwargs) -> CoderModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM coders'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = CoderModel(**resp)
			return resp

	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> CoderModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM coders'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetch(sql, *params)
			resp = [CoderModel(**x) for x in resp]
			return resp

	# Редактирование записи
	@staticmethod
	async def update(id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE coders'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)