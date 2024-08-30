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
@router.message(F.text == 'Сделать заказ')
async def create_order(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await message.answer('Выберите услугу которая вас интересует', reply_markup=kb_order_choose())

# Подать заявку на кодера\дизайнера
@router.message(F.text == 'Подать заявку в студию')
async def create_application(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await message.answer('Выберите кем хотите быть', reply_markup=kb_application_choose())


def message_tree_construct(req_type: str, req_sub_type: str, answers: dict, h1: bool = True):
	questions = req_questions.get(req_type, {}).get(req_sub_type, {})
	trns = {'order': 'Создание заказа\n', 'application': 'Создание заявки\n'}
	text = trns.get(req_type, '') if h1 else ''
	for i, question in enumerate(answers, start=1):
		prefix = '└ ' if i == len(answers) else '├ '
		endfix = '' if i == len(answers) else '\n'
		_text = answers[question] if isinstance(answers[question], str) else f'{len(answers[question])} файл{"ов" if len(answers[question]) in [0, 5, 6, 7, 8, 9] else "" if len(answers[question]) == 1 else "а" if len(answers[question]) >= 2 else ""}'
		text += f'{prefix}{questions.get(question, {}).get("q", question).replace(":", "")}: <code>{_text}</code>{endfix}'
	return text.replace('::', ':')

def get_question(req_type: str, req_sub_type: str, answers: dict = None, direction: str = 'next'):
	questions = req_questions.get(req_type, {}).get(req_sub_type, {})
	if answers is None: return questions
	questions_list = list(questions.keys())
	if len(answers) == 0:
		question = questions_list[0]
		return (question, questions.get(question), True, (len(questions_list) - 0) >= 0)
	elif len(questions) == 1:
		question = questions_list[0]
		return (question, questions.get(question), True, True)

	this_question = questions_list.index(list(answers.keys())[-1])
	if direction == 'prev': this_question_idx = this_question - 1
	elif direction == 'this': this_question_idx = this_question
	elif direction == 'next': this_question_idx = this_question + 1
	if (len(questions_list) - this_question_idx) <= 0:
		return (None, None, None, None)

	question = questions_list[this_question_idx]
	# question_key, question_data, is_first, is_last
	return (question, questions.get(question), this_question_idx == 0, (len(questions_list) - this_question_idx) >= 0)



@router.callback_query(F.data.startswith('order'))
async def callback_order(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	req_type = 'order'

	if cd[1] == 'chs': # Выбор вида заказа
		req_sub_type = cd[2]
		questions = get_question(req_type, req_sub_type)
		if len(questions) == 0:
			await call.answer('Неизвестный тип заказа, попробуй позже', show_alert=True)
			return
		await del_message(call.message)

		answers = {}
		files = {}
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await call.message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.set_state('input_order')
		await state.update_data(req_type=req_type, req_sub_type=req_sub_type, questions=questions, answers=answers, files=files, msgs=[call.message, msg])


@router.message(StateFilter('input_order'))
async def input_order(message: Message, bot: Bot, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()

	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})
	
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if mt == '↪ Назад':
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0:
			await del_message(*state_data.get('msgs', []), message)
			return await create_order(message, bot, state)
		if question_key in answers: del answers[question_key]
	elif question_data.get('is_file', False) and message.content_type not in ['text']:
		files[question_key] = [*files.get(question_key, []), message.message_id] if question_key in files else [message.message_id]
		msg = await message.reply('Файл добавлен', reply_markup=kb_back('continue', 'Продолжить'))
		await state.update_data(answers=answers, files=files, msgs=[*state_data.get('msgs'), message, msg])
		return
	elif question_data.get('skipable', False) and mt == '➡️ Пропустить':
		answers[question_key] = 'Пропущено'
	else:
		answers[question_key] = mt

	await del_message(*state_data.get('msgs', []), message)
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if not question_key:
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await message.answer(f'{text}\n\n<i>Создать заказ?</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.update_data(answers=answers, msgs=[msg])
		return


	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, msgs=[msg])


@router.callback_query(StateFilter('input_order'))
async def input_order_(call: CallbackQuery, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(call)
	cd = call.data.split(':')
	state_data = await state.get_data()

	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})

	await del_message(*state_data.get('msgs', []), call.message)
	old_question_key, old_question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if cd[0] == 'skip' and old_question_data.get('skipable', False):
		answers[old_question_key] = 'Пропущено'
	elif cd[0] == 'continue' and old_question_data.get('is_file', False):
		answers[old_question_key] = files.get(old_question_key, [])
	elif cd[0] == 'back':
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0:
			return await create_order(call.message, bot, state)
		if question_key in answers: del answers[question_key]
	elif not old_question_key:
		...
	else:
		if old_question_data.get('bool', False): answers[old_question_key] = ast.literal_eval(cd[0])
		else: answers[old_question_key] = cd[0]
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if not question_key:
		if (cd[0] == 'skip' and old_question_data.get('skipable', False)):
			text = message_tree_construct(req_type, req_sub_type, answers)
			msg = await call.message.answer(f'{text}\n\n<i>Создать заказ?</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
			await state.update_data(answers=answers, msgs=[msg])
			return
		else:
			if not ast.literal_eval(cd[0]):
				await call.answer('Создание заказа отменено', show_alert=True)
				return await create_order(call.message, bot, state)
			user = await Userx.get(tg_user_id=tg_user_id)
			request = await Requestx.add(user_id=user.id, rqst=[req_type, req_sub_type], questions_answers=json.dumps(answers))
			text = message_tree_construct(req_type, req_sub_type, answers, h1=False)
			msg = await call.message.answer(f'Заказ создан\nID заказа: <code>{request.uuid}</code>\n\n<b>📝 Информация о заказе:</b>\n{text}')
			await state.clear()
			return

	
	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await call.message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, files=files, msgs=[msg])



















@router.callback_query(F.data.startswith('application'))
async def callback_application(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	req_type = 'application'

	if cd[1] == 'chs': # Выбор вида заказа
		req_sub_type = cd[2]
		questions = get_question(req_type, req_sub_type)
		if len(questions) == 0:
			await call.answer('Неизвестный тип заявки, попробуй позже', show_alert=True)
			return
		await del_message(call.message)

		answers = {}
		files = {}
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await call.message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.set_state('input_application')
		await state.update_data(req_type=req_type, req_sub_type=req_sub_type, questions=questions, answers=answers, files=files, msgs=[call.message, msg])


@router.message(StateFilter('input_application'))
async def input_application(message: Message, bot: Bot, state: FSMContext):
	mt = message.text
	state_data = await state.get_data()

	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})
	
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if mt == '↪ Назад':
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0:
			await del_message(*state_data.get('msgs', []), message)
			return await create_application(message, bot, state)
		if question_key in answers: del answers[question_key]
	elif question_data.get('is_file', False) and message.content_type not in ['text']:
		files[question_key] = [*files.get(question_key, []), message.message_id] if question_key in files else [message.message_id]
		msg = await message.reply('Файл добавлен', reply_markup=kb_back('continue', 'Продолжить'))
		await state.update_data(answers=answers, files=files, msgs=[*state_data.get('msgs'), message, msg])
		return
	elif question_data.get('skipable', False) and mt == '➡️ Пропустить':
		answers[question_key] = 'Пропущено'
	else:
		answers[question_key] = mt

	await del_message(*state_data.get('msgs', []), message)
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if not question_key:
		text = message_tree_construct(req_type, req_sub_type, answers)
		msg = await message.answer(f'{text}\n\n<i>Создать заявку?</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
		await state.update_data(answers=answers, msgs=[msg])
		return


	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, msgs=[msg])


@router.callback_query(StateFilter('input_application'))
async def input_application_(call: CallbackQuery, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(call)
	cd = call.data.split(':')
	state_data = await state.get_data()

	req_type = state_data.get('req_type', None)
	req_sub_type = state_data.get('req_sub_type', None)
	questions = state_data.get('questions', {})
	answers = state_data.get('answers', {})
	files = state_data.get('files', {})

	await del_message(*state_data.get('msgs', []), call.message)
	old_question_key, old_question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if cd[0] == 'skip' and old_question_data.get('skipable', False):
		answers[old_question_key] = 'Пропущено'
	elif cd[0] == 'continue' and old_question_data.get('is_file', False):
		answers[old_question_key] = files.get(old_question_key, [])
	elif cd[0] == 'back':
		question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'this')
		if len(answers) == 0:
			return await create_application(call.message, bot, state)
		if question_key in answers: del answers[question_key]
	elif not old_question_key:
		...
	else:
		if old_question_data.get('bool', False): answers[old_question_key] = ast.literal_eval(cd[0])
		else: answers[old_question_key] = cd[0]
	question_key, question_data, is_first, is_last = get_question(req_type, req_sub_type, answers, 'next')
	if not question_key:
		if (cd[0] == 'skip' and old_question_data.get('skipable', False)):
			text = message_tree_construct(req_type, req_sub_type, answers)
			msg = await call.message.answer(f'{text}\n\n<i>Создать заявку?</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
			await state.update_data(answers=answers, msgs=[msg])
			return
		else:
			if not ast.literal_eval(cd[0]):
				await call.answer('Создание заявки отменено', show_alert=True)
				return await create_application(call.message, bot, state)
			user = await Userx.get(tg_user_id=tg_user_id)
			request = await Requestx.add(user_id=user.id, rqst=[req_type, req_sub_type], questions_answers=json.dumps(answers))
			text = message_tree_construct(req_type, req_sub_type, answers, h1=False)
			msg = await call.message.answer(f'Заявка создана\nID заявки: <code>{request.uuid}</code>\n\n<b>📝 Информация о заявке:</b>\n{text}')
			await state.clear()
			return

	
	text = message_tree_construct(req_type, req_sub_type, answers)
	msg = await call.message.answer(f'{text}\n\n<i>{question_data.get("q", question_key)}</i>', reply_markup=kb_multi_state(req_type, req_sub_type, questions, question_key, question_data))
	await state.update_data(answers=answers, files=files, msgs=[msg])
















@router.callback_query(F.data.startswith('user'))
async def callback_user(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	await state.clear()
	cd = custom_data.split(':') if custom_data else call.data.split(':')

	if cd[1] == 'req':
		if cd[2] == 'menu':
			await call.message.edit_text('Выберите кем хотите быть', reply_markup=kb_choose_profession())

		elif cd[2] == 'coder':
			await state.set_state('input_create_coder')
			this_state = 'age'
			msg = await call.message.edit_text('Заявка на кодера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_coder(this_state))
			await state.update_data(this_state=this_state, msgs=[msg])

		elif cd[2] == 'designer':
			await state.set_state('input_create_designer')
			this_state = 'age'
			msg = await call.message.edit_text('Заявка на дизайнера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_designer(this_state))
			await state.update_data(this_state=this_state, msgs=[msg])




# Ответы на вопросы
@router.message(F.text == 'Информация')
async def faq(message: Message, bot: Bot, state: FSMContext):
	await state.clear()

	await message.answer('Информация', disable_web_page_preview=True, reply_markup=kb_info())