# -*- coding: utf- 8 -*-
import time


# Форматирование запроса без аргументов
def sql_insert_format(sql, **kwargs) -> tuple[str, list]:
	if len(kwargs) > 1: sql += f"({', '.join([x for x in kwargs])})"
	else: sql += {', '.join([x for x in kwargs])}
	sql += ' VALUES '
	if len(kwargs) > 1: sql += f"({', '.join([f'${i}' for i, x in enumerate(kwargs, start=1)])})"
	else: sql += ', '.join([f'${i}' for i, x in enumerate(kwargs, start=1)])

	return sql, list(kwargs.values())

def sql_update_format(sql, **kwargs) -> tuple[str, list]:
	sql += ' SET '
	sql += ', '.join([f'{x} = ${i}' for i, x in enumerate(kwargs, start=1)])
	return sql, list(kwargs.values())


# Форматирование запроса с аргументами
def sql_where_format(sql, **kwargs) -> tuple[str, list]:
	sql += ' WHERE '

	sql += ' AND '.join([f'{item} = ${i}' for i, item in enumerate(kwargs, start=1)])

	return sql, list(kwargs.values())