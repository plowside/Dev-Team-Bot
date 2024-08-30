# -*- coding: utf- 8 -*-
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class UserModel(BaseModel):
	id: int
	tg_user_id: int
	tg_username: str | None = None
	tg_firstname: str | None = None
	referrer_from_user_id: int | None = None
	created_at: int | None = None


# Работа с юзером
class Userx:
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




	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> list[UserModel]:
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"SELECT * FROM {Userx.storage_name}"
			sql, parameters = sql_where_format(sql, kwargs)

			response = con.execute(sql, parameters).fetchall()

			if len(response) >= 1:
				response = [UserModel(**cache_object) for cache_object in response]

			return response

	# Получение всех записей
	@staticmethod
	def get_all() -> list[UserModel]:
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"SELECT * FROM {Userx.storage_name}"

			response = con.execute(sql).fetchall()

			if len(response) >= 1:
				response = [UserModel(**cache_object) for cache_object in response]

			return response



	# Удаление записи
	@staticmethod
	def delete(**kwargs):
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"DELETE FROM {Userx.storage_name}"
			sql, parameters = update_format_where(sql, kwargs)

			con.execute(sql, parameters)

	# Очистка всех записей
	@staticmethod
	def clear():
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"DELETE FROM {Userx.storage_name}"

			con.execute(sql)
