# -*- coding: utf- 8 -*-
import hashlib, secrets, string, httpx, random, time, uuid, pytz

from typing import Union
from datetime import datetime

from aiogram.types import Message, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from urllib.parse import urlencode

from data.config import *

################################### AIOGRAM ####################################

# Генерация реплай клавиатуры
def rkb_construct(*buttons, keyboard=None) -> ReplyKeyboardBuilder:
	if not keyboard:
		keyboard = ReplyKeyboardBuilder()

	for row in buttons:
		keyboard.row(*row)
	return keyboard

# Генерация реплай кнопки
def rkb(text: str) -> KeyboardButton:
	return KeyboardButton(text=text)

# Генерация инлайн клавиатуры
def ikb_construct(*buttons, back_button=None, keyboard=None) -> InlineKeyboardBuilder:
	if not keyboard:
		keyboard = InlineKeyboardBuilder()

	for row in buttons:
		keyboard.row(*row)
	if back_button:
		keyboard.row(back_button)
	return keyboard

# Генерация инлайн кнопки
def ikb(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
	if data is not None:
		return InlineKeyboardButton(text=text, callback_data=data)
	elif url is not None:
		return InlineKeyboardButton(text=text, url=url)

def get_user(message):
	return [message.from_user.id, (message.from_user.username.lower() if message.from_user.username is not None else "none"), message.from_user.first_name]

async def del_message(*messages) -> None:
	for message in messages:
		try:
			await message.delete()
		except:
			...
async def call_msg_answer(call, **kwargs):
	try: await call.message.edit_text(**kwargs)
	except:
		await call.message.answer(**kwargs)
		await del_message(call.message)

async def send_admin(bot, text, reply_markup=None):
	for user_id in admin_ids:
		try:
			await bot.send_message(user_id, text, reply_markup=reply_markup, disable_web_page_preview=True)
		except: ...

async def upload_file(bot, from_tg_id: int, message_id: int):
	msg = await bot.copy_message(filestorage_id, from_tg_id, message_id)
	return filestorage_id, msg.message_id



################################### MISC ###################################
async def get_bot_info(bot):
	return await bot.get_me()

def message_tree_construct(req_type: str, req_sub_type: str, answers: dict, h1: bool = True):
	questions = req_questions.get(req_type, {}).get(req_sub_type, {})
	trns = trns_all.get('h1', {})
	if h1:
		text = f"{trns.get(req_type, '').get('header')}\n"
		if len(answers) > 0: text += f"├ {trns.get(req_type, '').get('req_name').format(req_type_trns=trns_all.get('kb_admin_requests', {}).get('q', {}).get(req_type, {}).get(req_sub_type, 'Неизвестная'))}\n"
		else: text += f"└ {trns.get(req_type, '').get('req_name').format(req_type_trns=trns_all.get('kb_admin_requests', {}).get('q', {}).get(req_type, {}).get(req_sub_type, 'Неизвестная'))}"
	else:
		text = ''
	for i, question in enumerate(answers, start=1):
		prefix = '└ ' if i == len(answers) else '├ '
		endfix = '' if i == len(answers) else '\n'
		_text = answers[question] if isinstance(answers[question], str) else ('Да' if answers[question] else 'Нет') if isinstance(answers[question], bool) else f'{len(answers[question])} файл{"ов" if len(answers[question]) in [0, 5, 6, 7, 8, 9] else "" if len(answers[question]) == 1 else "а" if len(answers[question]) >= 2 else ""}'
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

def paginate_list(lst: list, items_per_page: int, current_page: int = 0):
	start_idx = current_page * items_per_page
	end_idx = start_idx + items_per_page
	return lst[start_idx:end_idx]

def is_uuid4(text):
    try:
        uuid_obj = uuid.UUID(text, version=4)
        return True
    except ValueError:
        return False

def gen_txn(length = 16) -> int:
	return (''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))).upper()

def get_unix():
	return int(time.time())

def clear_html(get_text: str) -> str:
	if get_text is not None:
		if "<" in get_text: get_text = get_text.replace("<", "*")
		if ">" in get_text: get_text = get_text.replace(">", "*")
	else:
		get_text = ""

	return get_text

def parse_num(num, is_float: bool = False) -> Union[int, float]:
	try: return float(num.replace(',', '.')) if is_float else int(float(num.replace(',', '.')))
	except: return None

def user_format_url(user_id, username):
	return (f'<a href="t.me/{username}">{username}</a>' if username not in ['none', None] else f'<a href="tg://user?id={user_id}">None</a>')

def date_to_text(date, text_format = '%d.%m.%Y %H:%M'):
	if isinstance(date, int): return datetime.strftime(datetime.fromtimestamp(date), text_format)
	else: return datetime.strftime(date, text_format)

def time_to_text(seconds, is_full = False):
	seconds = int(seconds)
	days = seconds // 86400
	hours = (seconds - days * 86400) // 3600
	minutes = (seconds % 3600) // 60
	remaining_seconds = seconds % 60
	formatted_time = ""

	if is_full:
		if days > 0: formatted_time += f'{days} {morpher(days, "дней")} '
		if hours > 0: formatted_time += f'{hours} {morpher(hours, "часов")} '
		if minutes > 0: formatted_time += f'{minutes} {morpher(minutes, "минут")} '
	else:
		if days > 0: formatted_time += f'{days} {morpher(days, "дней")} '
		if hours > 0: formatted_time += f'{hours} {morpher(hours, "часов")} '
		if minutes > 0: formatted_time += f'{minutes} {morpher(minutes, "минут")} '
		if remaining_seconds > 0: formatted_time += (f'{remaining_seconds} {morpher(remaining_seconds, "секунд")}')
	if formatted_time == '': formatted_time = 'меньше минуты'
	return formatted_time.strip()

def morpher(num, presset="час", cases=None):
	pressets = {
		'днейднядень':				{'nom': 'день',		'gen': 'дня',		'plu': 'дней'},
		'часовчасычас':				{'nom': 'час',		'gen': 'часа',		'plu': 'часов'},
		'минутминутыминута':		{'nom': 'минута',	'gen': 'минуты',	'plu': 'минут'},
		'секундсекундысекунда':		{'nom': 'секунда',	'gen': 'секунды',	'plu': 'секунд'},
		'сервисовсервисасервис':	{'nom': 'сервис',	'gen': 'сервиса',	'plu': 'сервисов'},
		'рублейрублярубль':			{'nom': 'рубль',	'gen': 'рубля',		'plu': 'рублей'},
		'задачзадачизадача':		{'nom': 'задача',	'gen': 'задачи',	'plu': 'задач'},
		'номеровномераномер':		{'nom': 'номер',	'gen': 'номера',	'plu': 'номеров'},
	}
	if cases == None:
		cases = [pressets[x] for x in pressets if presset in x][0]

	z = {0: 'nom', 1: 'gen', 2: 'plu'}
	if type(cases) is not dict:
		cases_ = cases
		cases = {}
		for i, x in enumerate(cases_):
			cases[z[i]] = x
	num = abs(num)
	word = ''
	if '.' in str(num):
		word = cases['gen']
	else:
		last_two_digits = num % 100
		last_digit = num % 10

		if last_digit >= 2 and last_digit <= 4 and last_two_digits >= 20: word = cases['gen']
		elif last_digit >= 2 and last_digit <= 4 and last_two_digits <= 10: word = cases['gen']
		elif (last_digit == 1 and last_two_digits != 11) or (last_digit >= 2 and last_digit <= 4 and (last_two_digits < 10 or last_two_digits >= 20)): word = cases['nom']
		else: word = cases['plu']

	return word