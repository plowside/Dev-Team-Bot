# -*- coding: utf- 8 -*-
import asyncio, json, ast

from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.config import *
from database import *
from utils.functions import *
from keyboards import *
from .. import main_start

router = Router(name=__name__)






################################################################################
################################### MESSAGE ####################################

# Сделать заказ
@router.message(F.text == '🔥 Сделать заказ')
async def create_order(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await message.answer('<b>🔥 Сделать заказ</b>\n└ Услуга: <code>Не выбрана</code>\n\n<i>♦️ Выберите один из предложенных вариантов.</i>', reply_markup=kb_order_choose())

# Подать заявку на кодера\дизайнера
@router.message(F.text == '💼 Вступить в студию')
async def create_application(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await message.answer('<b>💼 Вступить в студию</b>\n└ Должность: <code>Не выбрана</code>\n\n<i>♦️ Выберите один из предложенных вариантов.</i>ь', reply_markup=kb_application_choose())


@router.callback_query(F.data.startswith('req'))
async def callback_req(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	req_type = cd[1]

	if cd[2] == 'chs': # Выбор вида заказа
		req_sub_type = cd[3]
		questions = get_question(req_type, req_sub_type)
		if len(questions) == 0:
			await call.answer('Неизвестный тип заказа, попробуйте позже', show_alert=True)
			return
		# await del_message(call.message)

		answers = {}
		files = {}
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await call.message.edit_text(f'{text}\n\n{question_data.get("user_q", question_key)}', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.set_state('input_req')

		await state.update_data(req_type=req_type, req_sub_type=req_sub_type, questions=questions, answers=answers, files=files, msgs=[call.message, msg])


@router.message(StateFilter('input_req'))
async def input_req(message: Message, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(message)
	mt = message.text
	state_data = await state.get_data()
	
	trns = trns_all.get('morph', {})
	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})
	this_trns = trns.get(req_type, {})
	
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if mt == '↪ Назад': # Назад
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0: # Переход в главное меню
			await del_message(*state_data.get('msgs', []), message)
			return await create_order(message, bot, state) if req_type == 'order' else await create_application(message, bot, state)
		if question_key in answers: del answers[question_key]
	elif question_data and question_data.get('is_file', False) and message.content_type not in ['text']: # Добавление файла
		await state.update_data(answers=answers, files=files)
		file_chat_id, file_message_id = await upload_file(bot, tg_user_id, message.message_id)
		files[question_key] = [*files.get(question_key, []), file_message_id] if question_key in files else [file_message_id]
		msg = await message.reply('Файл добавлен', reply_markup=kb_back('continue', 'Продолжить'))
		state_data = await state.get_data()
		await state.update_data(msgs=[*state_data.get('msgs', []), message, msg])
		return
	elif not question_key:
		...
	else:
		answers[question_key] = mt

	await del_message(*state_data.get('msgs', []), message)
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if not question_key:
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await message.answer(f'{text}\n\nСоздать {this_trns.get("l", {}).get("v", "")}?', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.update_data(answers=answers, msgs=[msg])
		return

	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await message.answer(f'{text}\n\n{question_data.get("user_q", question_key)}', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, msgs=[msg])


@router.callback_query(StateFilter('input_req'))
async def input_req_(call: CallbackQuery, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(call)
	cd = call.data.split(':')
	state_data = await state.get_data()

	trns = trns_all.get('morph', {})
	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})
	this_trns = trns.get(req_type, {})

	old_question_key, old_question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')

	if cd[0] == 'skip' and old_question_data.get('skipable', False): # Пропустить вопрос
		answers[old_question_key] = 'Пропущено'
	elif cd[0] == 'continue' and old_question_data.get('is_file', False): # Закончить загрузку файлов
		await del_message(*state_data.get('msgs', []))
		answers[old_question_key] = files.get(old_question_key, [])
	elif cd[0] == 'back': # Назад
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0: # В главное меню
			await del_message(*state_data.get('msgs', []), call.message)
			return await create_order(call.message, bot, state) if req_type == 'order' else await create_application(call.message, bot, state)
		if question_key in answers: del answers[question_key]
	elif not old_question_key: # Создание заявки
		...
	else: # Быстрый выбор ответа
		if old_question_data.get('bool', False): answers[old_question_key] = ast.literal_eval(cd[0])
		else: answers[old_question_key] = cd[0]
	
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	this_question_key, this_question_data, this_is_first, this_is_last = get_question(req_type, req_sub_type, answers, 'this')
	if not question_key:
		if (cd[0] == 'skip' and old_question_data.get('skipable', False)) or (cd[0] == 'continue' and old_question_data.get('is_file', False)): # Сообщение с проверкой создание заявки
			text = message_tree_construct(req_type, req_sub_type, answers)
			msg = await call_msg_answer(call, text=f'{text}\n\nСоздать {this_trns.get("l", {}).get("v", "")}?', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
			await state.update_data(answers=answers, msgs=[msg])
			return
		else: # Создание заявки
			await state.clear()
			try: # Отмена
				if not ast.literal_eval(cd[0]):
					await call.answer(f'Создание {this_trns.get("l", {}).get("r", "")} отменено', show_alert=True)
					return await create_order(call.message, bot, state) if req_type == 'order' else await create_application(call.message, bot, state)
			except:
				text = message_tree_construct(req_type, req_sub_type, answers)
				msg = await call_msg_answer(call, text=f'{text}\n\nСоздать {this_trns.get("l", {}).get("v", "")}?', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
				await state.update_data(answers=answers, msgs=[msg])
				return
			user = await Userx.get(tg_user_id=tg_user_id)
			request = await Requestx.add(user_id=user.id, req_type=req_type, req_sub_type=req_sub_type, questions_answers=json.dumps(answers))
			text = message_tree_construct(req_type, req_sub_type, answers, h1=False)
			msg = await call_msg_answer(call, text=f'{this_trns.get("u", {}).get("i", "")} создан{this_trns.get("end", {}).get("zh", "")}\nID {this_trns.get("u", {}).get("r", "")}: <code>{request.uuid}</code>\n\n<b>📝 Информация о {this_trns.get("l", {}).get("p", "")}:</b>\n{text}')
			await send_admin(bot, f'<b>Нов{this_trns.get("end", {}).get("n", "")} {this_trns.get("l", {}).get("i", "")}</b>\n├ ID {this_trns.get("l", {}).get("i", "")}:  <code>{request.uuid}</code>\n└ TG ID Пользователя:  <code>{user.tg_user_id}</code>', reply_markup=kb_back(f'admin:request:s:{request.id}', f'Открыть {this_trns.get("l", {}).get("v", "")}'))
			return
	
	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await call_msg_answer(call, text=f'{text}\n\n{question_data.get("user_q", question_key)}', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, files=files, msgs=[msg])










# Ответы на вопросы
@router.message(F.text == 'ℹ️ Информация')
async def faq(message: Message, bot: Bot, state: FSMContext):
	await state.clear()

	await message.answer('<b>💻 KILLA STUDIO — Команда профессионалов.</b>\nМы верим, что каждая деталь важна, и стремимся создавать решения, которые вдохновляют, удивляют и приносят пользу. Вне зависимости от того, нужен ли вам стильный и функциональный веб-сайт, мобильное приложение или креативный дизайн, мы готовы взяться за проект любой сложности.', disable_web_page_preview=True, reply_markup=kb_info())