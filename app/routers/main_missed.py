# -*- coding: utf- 8 -*-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import *
from data.config import *
from loader import custom_fsm
from utils.filters import IsDialogue
from utils.functions import *

router = Router(name=__name__)


# Колбэк с обработкой кнопки
@router.callback_query(F.data == '...')
async def main_missed_callback_answer(call: CallbackQuery, bot: Bot, state: FSMContext):
	await call.answer(cache_time=60)


# Обработка всех колбэков которые потеряли стейты после перезапуска скрипта
@router.callback_query(StateFilter('*'))
async def main_missed_callback(call: CallbackQuery, bot: Bot, state: FSMContext):
	await call.answer('❗️ Кнопка недействительна. Повторите действия заново', True)

@router.message(IsDialogue())
async def main_dialogue(message: Message, bot: Bot, state: FSMContext):
	tg_user_id = message.from_user.id
	dialogue_obj = custom_fsm['dialogue'][tg_user_id]
	user = dialogue_obj['user']
	admin = dialogue_obj['admin']
	dialogue = dialogue_obj['dialogue']

	if message.content_type == 'text':
		text = message.html_text.replace(str(user.tg_user_id), "").replace(f'@{user.tg_username}', "").replace(str(user.tg_username), "") if admin.tg_user_id in moderator_ids else message.html_text
		await bot.send_message(admin.tg_user_id, text)
		message_id = message.message_id
	else:
		file_chat_id, file_message_id = await upload_file(bot, user.tg_user_id, message.message_id)
		message_id = file_message_id
		await bot.copy_message(chat_id=admin.tg_user_id, from_chat_id=file_chat_id, message_id=message_id)
	await DialogueMessagex.add(dialogue_id=dialogue.id, message_id=message_id, message_content_type=message.content_type, message_text=message.html_text, from_user_id=user.id, from_user_tg_id=user.tg_user_id, from_user_type='user')