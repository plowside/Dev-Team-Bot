# -*- coding: utf- 8 -*-
from aiogram import Router
from aiogram.filters import ExceptionMessageFilter
from aiogram.handlers import ErrorHandler

from utils.logging import logging

router = Router(name=__name__)


# Ошибка с редактированием одинакового сообщения
@router.errors()
class MyHandler(ErrorHandler):
	async def handle(self):
		logging.exception(f"====================\nException name: {self.exception_name}\nException message: {self.exception_message}\n====================")
