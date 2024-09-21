# -*- coding: utf- 8 -*-
from aiogram import Bot, BaseMiddleware
from aiogram.types import User

from database import Userx
from utils.functions import *

# Проверка юзера в БД и его добавление
class ExistsUserMiddleware(BaseMiddleware):
	def __init__(self, bot):
		self.bot = bot

	async def __call__(self, handler, event, data):
		this_user: User = data.get("event_from_user")

		if not this_user.is_bot:
			get_user = await Userx.get(tg_user_id=this_user.id)

			user_id = this_user.id
			username = this_user.username
			firstname = clear_html(this_user.full_name)

			if username is None: username = ''
			if firstname is None: firstname = ''

			if get_user is None:
				try:
					if event.text.startswith('/start'):
						message_args = event.text.split(' ')
						if len(message_args) > 1:
							if message_args[1].startswith('ref_'):
								referrer_user_id = await Userx.get(tg_user_id=int(message_args[1][4:]))
								if referrer_user_id: referrer_user_id = referrer_user_id.id

					referrer_user_id
				except: referrer_user_id = None
				await Userx.add(user_id, username.lower(), firstname, referrer_from_user_id=referrer_user_id)
				await send_admin(self.bot, f'<b>🔔 Новый пользователь!\n\n👤 Username: {user_format_url(tg_user_id=this_user.id, tg_username=this_user.username)}\n🆔 Telegram ID: <code>{this_user.id}</code></b>')
			else:
				if username.lower() != get_user.tg_username:
					Userx.update(get_user.id, tg_firstname=username.lower())
				
				if firstname != get_user.tg_firstname:
					Userx.update(get_user.id, tg_username=firstname)


		return await handler(event, data)