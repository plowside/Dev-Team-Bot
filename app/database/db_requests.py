# -*- coding: utf- 8 -*-
import uuid, json
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class RequestModel(BaseModel):
	id: int
	uuid: str
	user_id: int
	req_type: str
	req_sub_type: str
	questions_answers: str
	completed: bool
	created_at: int

# Работа с юзером
class Requestx:
	model = RequestModel

	# Добавление записи
	@staticmethod
	async def add(user_id: int, req_type: str, req_sub_type: str, questions_answers: dict, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO requests'
			sql, params = sql_insert_format(sql, user_id=user_id, req_type=req_type, req_sub_type=req_sub_type, questions_answers=questions_answers, uuid=str(uuid.uuid4()), created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = RequestModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(order_by: str = None, **kwargs) -> RequestModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM requests'
			sql, params = sql_where_format(sql, **kwargs)
			if order_by: sql += f' ORDER BY {order_by}'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = RequestModel(**resp)
				resp.questions_answers = json.loads(resp.questions_answers)
			return resp

	# Получение записей
	@staticmethod
	async def gets(order_by: str = None, **kwargs) -> RequestModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM requests'
			sql, params = sql_where_format(sql, **kwargs)
			if order_by: sql += f' ORDER BY {order_by}'
			resp = await conn.fetch(sql, *params)
			resp = [RequestModel(**x) for x in resp]
			for x in resp:
				x.questions_answers = json.loads(x.questions_answers)
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

		return await Requestx.get(id=id)

	@staticmethod
	async def delete(**kwargs):
		async with db.pool.acquire() as conn:
			sql = 'DELETE FROM requests'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.execute(sql, *params)