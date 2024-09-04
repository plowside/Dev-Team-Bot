# -*- coding: utf- 8 -*-
from pydantic import BaseModel
from typing import Optional

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class UserModel(BaseModel):
	id: int
	tg_user_id: int
	tg_username: Optional[str] = None
	tg_firstname: Optional[str] = None
	referrer_from_user_id: Optional[int] = None
	created_at: Optional[int] = None


# Работа с юзером
class Userx:
	model = UserModel
	# Добавление записи
	@staticmethod
	async def add(user_id: int, username: str, firstname: str, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = f'INSERT INTO users'
			sql, params = sql_insert_format(sql, tg_user_id=user_id, tg_username=username, tg_firstname=firstname, created_at=unix, **kwargs)
			resp = await conn.fetchrow(sql, *params)

		return await Userx.get(tg_user_id=user_id)

	# Получение записи
	@staticmethod
	async def get(any_value = False, **kwargs) -> UserModel:
		async with db.pool.acquire() as conn:
			sql = f'SELECT * FROM users'
			sql, params = sql_where_format(sql, **kwargs)
			if any_value:
				sql = sql.replace('AND', 'OR')

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = UserModel(**resp)
			return resp

	# Редактирование записи
	@staticmethod
	async def update(user_id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE users'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(user_id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)