# -*- coding: utf- 8 -*-
import uuid
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class RequestModel(BaseModel):
	id: int
	uuid: str
	user_id: int
	rqst: str
	questions_answers: str
	completed: bool
	created_at: int

# Работа с юзером
class Requestx:
	# Добавление записи
	@staticmethod
	async def add(user_id: int, rqst: str, questions_answers: dict, **kwargs):
		unix = get_unix()
		if isinstance(rqst, list):
			rqst = ':'.join(rqst)
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO requests'
			sql, params = sql_insert_format(sql, user_id=user_id, rqst=rqst, questions_answers=questions_answers, uuid=str(uuid.uuid4()), created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = RequestModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(**kwargs) -> RequestModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM requests'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = RequestModel(**resp)
			return resp

	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> RequestModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM requests'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetch(sql, *params)
			resp = [RequestModel(**x) for x in resp]
			return resp

	# Редактирование записи
	@staticmethod
	async def update(id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE requests'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)