# -*- coding: utf- 8 -*-
from pydantic import BaseModel

from .database import db
from .db_helper import *
from utils.functions import get_unix


# Модель таблицы
class OrderModel(BaseModel):
	id: int
	user_id: int
	point_of_work: str
	deadline: str
	budget: str
	completed: bool
	created_at: int

# Работа с юзером
class Orderx:
	# Добавление записи
	@staticmethod
	async def add(user_id: int, point_of_work: str, deadline: str, budget: str, **kwargs):
		unix = get_unix()
		async with db.pool.acquire() as conn:
			sql = 'INSERT INTO orders'
			sql, params = sql_insert_format(sql, user_id=user_id, point_of_work=point_of_work, deadline=deadline, budget=budget, created_at=unix, **kwargs)
			sql = f'{sql} RETURNING *'
			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = OrderModel(**resp)
		return resp

	# Получение записи
	@staticmethod
	async def get(**kwargs) -> OrderModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM orders'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetchrow(sql, *params)
			if resp:
				resp = OrderModel(**resp)
			return resp

	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> OrderModel:
		async with db.pool.acquire() as conn:
			sql = 'SELECT * FROM orders'
			sql, params = sql_where_format(sql, **kwargs)

			resp = await conn.fetch(sql, *params)
			resp = [OrderModel(**x) for x in resp]
			return resp

	# Редактирование записи
	@staticmethod
	async def update(id, **kwargs):
		async with db.pool.acquire() as conn:
			sql = 'UPDATE orders'
			sql, params = sql_update_format(sql, **kwargs)

			params.append(id)
			sql += f' WHERE id = ${len(kwargs)+1}'

			resp = await conn.execute(sql, *params)




	# Получение записей
	@staticmethod
	async def gets(**kwargs) -> list[OrderModel]:
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"SELECT * FROM {Orderx.storage_name}"
			sql, parameters = sql_where_format(sql, kwargs)

			response = con.execute(sql, parameters).fetchall()

			if len(response) >= 1:
				response = [OrderModel(**cache_object) for cache_object in response]

			return response

	# Получение всех записей
	@staticmethod
	def get_all() -> list[OrderModel]:
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"SELECT * FROM {Orderx.storage_name}"

			response = con.execute(sql).fetchall()

			if len(response) >= 1:
				response = [OrderModel(**cache_object) for cache_object in response]

			return response



	# Удаление записи
	@staticmethod
	def delete(**kwargs):
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"DELETE FROM {Orderx.storage_name}"
			sql, parameters = update_format_where(sql, kwargs)

			con.execute(sql, parameters)

	# Очистка всех записей
	@staticmethod
	def clear():
		with sqlite3.connect(PATH_DATABASE) as con:
			con.row_factory = dict_factory
			sql = f"DELETE FROM {Orderx.storage_name}"

			con.execute(sql)
