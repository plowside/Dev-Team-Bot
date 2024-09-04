# -*- coding: utf- 8 -*-
import asyncio, random, json

from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from loader import dp, bot, custom_fsm
from data.config import *
from database import *
from utils.functions import *
from keyboards import *
from .. import main_start

router = Router(name=__name__)





################################################################################
################################### MESSAGE ####################################

@router.callback_query(F.data.startswith('admin'))
async def callback_admin(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	cd = custom_data.split(':') if custom_data else call.data.split(':')
	tg_user_id, username, firstname = get_user(call)


	if cd[1] == 'menu':
		await call.message.edit_text('🧑🏻‍💻 Админ меню', reply_markup=kb_admin_menu(tg_user_id))

	elif cd[1] == 'search':
		if len(cd) == 2:
			await state.set_state('input_user_search')
			msg = await call.message.edit_text('<b>👤 Поиск пользователя</b>\n<i>Введите user_id\\tg_id\\username\\uuid запроса пользователя</i>', reply_markup=kb_admin_search())
			await state.update_data(msg=msg)
		else:
			user_id = int(cd[2])
			user = await Userx.get(id=user_id)
			if not user:
				await call.answer('❌ Не удалось найти пользователя', show_alert=True)
				return

			reg_date = datetime.fromtimestamp(user.created_at).strftime("%d.%m.%Y")
			if tg_user_id in moderator_ids:
				await call.message.edit_text(f'<b>Информация о пользователе</b>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(tg_user_id, user.id))
			else:
				await call.message.edit_text(f'<b>Информация о пользователе</b>\n├ Юзернейм: {user_format_url(user)}\n├ ID телеграма:  <code>{user.tg_user_id}</code>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(tg_user_id, user.id))
	
	elif cd[1] == 'dialogue':
		act = cd[2]
		user_id = int(cd[3])
		user = await Userx.get(id=user_id)
		admin = await Userx.get(tg_user_id=tg_user_id)

		if act == 'menu':
			dialogue = await Dialoguex.get(admin_user_id=admin.id, user_id=user.id, show=True)
			await call.message.edit_text('Меню диалога с пользователем', reply_markup=kb_admin_user_dialogue(admin.tg_user_id, user.id, dialogue.id if dialogue else None))

		elif act == 'start':
			try: result = await bot.send_message(user.tg_user_id, f'Администратор начал с вами чат, все ваши сообщения будет получать администратор.')
			except: result = False
			if not result:
				await call.answer('🔐 Пользователь заблокировал бота', show_alert=True)
				return

			await send_admin(bot, f'<b>✍️ {"Модератор" if tg_user_id in moderator_ids else "Админ"} начал диалог с пользователем</b>\n├ TG ID Пользователя:  <code>{user.tg_user_id}</code>\n├ TG ID {"Модераторора" if tg_user_id in moderator_ids else "Админа"}:  <code>{admin.tg_user_id}</code>', reply_markup=kb_back(f'admin:search:{user.id}', '🔍 Найти Пользователя'))
			dialogues = await Dialoguex.gets(admin_user_id=admin.id, user_id=user.id, show=True)
			for dialogue in dialogues:
				await Dialoguex.update(dialogue.id, show=False)

			dialogue = await Dialoguex.add(admin_user_id=admin.id, user_id=user.id, show=True)
			custom_fsm['dialogue'][user.tg_user_id] = {'user': user, 'admin': admin, 'dialogue': dialogue, 'history': []}
			await state.set_state('user_dialogue')
			await state.update_data(user=user, admin=admin, dialogue=dialogue)
			await call.answer()
			await call.message.answer(f'Вы начали диалог с пользователем', reply_markup=kb_admin_dialogue())

		elif act == 'continue':
			dialogue_id = int(cd[4])
			dialogue = await Dialoguex.get(id=dialogue_id, show=True)
			await send_admin(bot, f'<b>✍️ {"Модератор" if tg_user_id in moderator_ids else "Админ"} начал диалог с пользователем</b>\n├ TG ID Пользователя:  <code>{user.tg_user_id}</code>\n├ TG ID {"Модераторора" if tg_user_id in moderator_ids else "Админа"}:  <code>{admin.tg_user_id}</code>', reply_markup=kb_back(f'admin:search:{user.id}', '🔍 Найти Пользователя'))
			if not dialogue:
				return await call.answer('❌ Не удалось получить историю диалога\nНачните новый диалог', show_alert=True)
			elif admin.tg_user_id in moderator_ids and (dialogue.admin_user_id != admin.id or dialogue.user_id != user.id):
				return await call.answer('Это не ваш диалог, начните новый', show_alert=True)

			try: result = await bot.send_message(user.tg_user_id, f'Администратор начал с вами чат, все ваши сообщения будет получать администратор.')
			except: result = False
			if not result:
				await call.answer('🔐 Пользователь заблокировал бота', show_alert=True)
				return

			dialogue_history = await DialogueMessagex.gets(dialogue_id=dialogue.id)
			if len(dialogue_history) > 0:
				await bot.send_message(chat_id=admin.tg_user_id, text=f'<i>📝 История диалога (<code>{len(dialogue_history)} шт.</code>)</i>')
				for message in dialogue_history:
					prefix = f'<b>👤 Пользователь</b>' if message.from_user_type == 'user' else '<b>🐓 Админ</b>'	
					if message.message_content_type == 'text' and message.message_text:
						text = message.message_text.replace(str(admin.tg_user_id), "").replace(f'@{admin.tg_username}', "").replace(str(admin.tg_username), "")
						text = f'{prefix}\n\n{text}' if admin.tg_user_id in moderator_ids else f'{prefix}\n\n{message.message_text}'
						await bot.send_message(chat_id=admin.tg_user_id, text=text)
					else:
						await bot.copy_message(chat_id=admin.tg_user_id, from_chat_id=filestorage_id, message_id=message.message_id, caption=prefix)

			custom_fsm['dialogue'][user.tg_user_id] = {'user': user, 'admin': admin, 'dialogue': dialogue, 'history': []}
			await state.set_state('user_dialogue')
			await state.update_data(user=user, admin=admin, dialogue=dialogue)
			await call.answer()
			await call.message.answer(f'Вы продолжили диалог с пользователем', reply_markup=kb_admin_dialogue())

		elif act == 'history':
			dialogues = await Dialoguex.gets(user_id=user.id)
			if len(dialogues) == 0:
				return await call.answer('🗑 История диалогов пустая', show_alert=True)

			await call.message.edit_text(f'<i>🗄 История диалогов (<code>{len(dialogues)} шт.</code>)</i>', reply_markup=kb_admin_user_dialogues(user.id, dialogues))
		
		elif act == 'clear_history':
			dialogues = await Dialoguex.gets(user_id=user.id)
			for dialogue in dialogues:
				await DialogueMessagex.delete(dialogue_id=dialogue.id)
			await Dialoguex.delete(user_id=user.id)
			await call.answer('🗑 История очищена', show_alert=True)
			return await callback_admin(call, bot, state, f'admin:dialogue:menu:{user.id}')
		
		elif act == 'show':
			dialogue_id = int(cd[4])
			dialogue = await Dialoguex.get(id=dialogue_id)

			await del_message(call.message)
			dialogue_history = await DialogueMessagex.gets(dialogue_id=dialogue.id)
			await bot.send_message(chat_id=tg_user_id, text=f'<i>📝 История диалога (<code>{len(dialogue_history)} шт.</code>)</i>\n├ ID админа:  <code>{dialogue.admin_user_id}</code>\n└ ID пользователя:  <code>{dialogue.user_id}</code>', reply_markup=kb_back(f'admin:search:{dialogue.admin_user_id}', '🔍 Найти админа'))
			if len(dialogue_history) > 0:
				for message in dialogue_history:
					prefix = f'<b>👤 Пользователь</b>' if message.from_user_type == 'user' else '<b>🐓 Админ</b>'	
					if message.message_content_type == 'text' and message.message_text:
						text = f'{prefix}\n\n{message.message_text}'
						await bot.send_message(chat_id=tg_user_id, text=text)
					else:
						await bot.copy_message(chat_id=tg_user_id, from_chat_id=filestorage_id, message_id=message.message_id, caption=prefix)

			await call.message.answer('<i>🚧 Конец диалога 🚧</i>', reply_markup=kb_back(f'admin:dialogue:history:{user_id}'))

	elif cd[1] == 'request':
		act = cd[2]
		req_id = int(cd[3])
		req_status = int(cd[4]) if len(cd) >= 5 else 0
		req_type = int(cd[5]) if len(cd) >= 6 else 0
		page = int(cd[6]) if len(cd) >= 7 else 0
		user_id = int(cd[7]) if len(cd) >= 8 else None

		if act == 's': # Показать запрос
			req = await Requestx.get(id=req_id)
			files = [z for x in req.questions_answers.values() if isinstance(x, list) for z in x]
			text = message_tree_construct(req_type=req.req_type, req_sub_type=req.req_sub_type, answers=req.questions_answers, h1=False)
			await call.message.edit_text(f'<b>{"🔴" if req.completed else "🟢"} Информация о {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("p", "запросе")}</b>\n├ UUID {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("r", "запроса")}:  <code>{req.uuid}</code>\n│\n{text}', reply_markup=kb_admin_request(tg_user_id, req, files, req_status, req_type, page, user_id))
		
		elif act == 'gf': # Получить файлы
			req = await Requestx.get(id=req_id)
			user = await Userx.get(id=req.user_id)
			await call.answer('🔄 Выгружаю файлы...')
			await call.message.edit_text(f'<b>🚧 Файлы {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("r", "запроса")} 🚧</b>')

			files = {key: value for key, value in req.questions_answers.items() if isinstance(value, list)}
			for q, files_per_q in files.items():
				await call.message.answer(f'<i>🗂 Файлы для <b>{req_questions.get(req.req_type, {}).get(req.req_sub_type, {}).get(q, {}).get("q", q)}</b></i>')
				for file in files_per_q:
					try: await bot.copy_message(chat_id=tg_user_id, from_chat_id=filestorage_id, message_id=file)
					except: await call.message.answer('<b>❌ Не удалось найти файл в хранилище</b>')
			# await del_message(call.message)
			text = message_tree_construct(req_type=req.req_type, req_sub_type=req.req_sub_type, answers=req.questions_answers, h1=False)
			await call.message.answer(f'<b>{"🔴" if req.completed else "🟢"} Информация о {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("p", "запросе")}</b>\n{text}', reply_markup=kb_admin_request(tg_user_id, req, files, req_status, req_type, page, user_id))


		elif act == 'c': # Пометить запрос как завершенный
			req = await Requestx.update(id=req_id, completed=True)

			await call.answer(f'{trns_all.get("morph", {}).get(req.req_type, {}).get("u", {}).get("i", "Запрос")} отмечен{trns_all.get("morph", {}).get(req.req_type, {}).get("end", {}).get("zh", "")} как завершенн{trns_all.get("morph", {}).get(req.req_type, {}).get("end", {}).get("n", "ый")}', show_alert=True)
			await callback_admin(call, bot, state, f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')

		elif act == 'd': # Удалить запрос
			await Requestx.delete(id=req_id)
			await callback_admin(call, bot, state, f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')

	elif cd[1] == 'request_search':
		req_status = int(cd[2]) if len(cd) >= 3 else 0
		req_type = int(cd[3]) if len(cd) >= 4 else 0
		page = int(cd[4]) if len(cd) >= 5 else 0
		user_id = int(cd[5]) if len(cd) >= 6 else None

		await state.set_state('input_request_search')
		msg = await call.message.edit_text('<i>🔍 Введите id\\uuid запроса</i>', reply_markup=kb_back(f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}'))
		await state.update_data(req_status=req_status, req_type=req_type, page=page, user_id=user_id, msg=msg)

	elif cd[1] == 'requests':
		req_status = int(cd[2]) if len(cd) >= 3 else 0
		req_type = int(cd[3]) if len(cd) >= 4 else 0
		page = int(cd[4]) if len(cd) >= 5 else 0
		user_id = int(cd[5]) if len(cd) >= 6 else None

		requests = await Requestx.gets(user_id=user_id, req_type={2: 'application', 1: 'order', 0: None}.get(req_type, None), completed={2: True, 1: False, 0: None}.get(req_status, None), order_by='id DESC')
		items_for_page = paginate_list(requests, 6, page)
		await call.message.edit_text(f'Все запросы', reply_markup=kb_admin_requests(items_for_page, req_status, req_type, (len(paginate_list(requests, 6, page - 1)) > 0, page, len(paginate_list(requests, 6, page + 1)) > 0), user_id))

@router.message(StateFilter('input_request_search'))
async def input_request_search(message: Message, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(message)
	mt = message.text.strip().replace('@', '')
	state_data = await state.get_data()
	await del_message(message, state_data.get('msg', None))
	req_status = state_data.get('req_status', 0)
	req_type = state_data.get('req_type', 0)
	page = state_data.get('page', 0)
	user_id = state_data.get('user_id', None)

	if mt.isnumeric():
		mt = int(mt)
		req = await Requestx.get(id=mt)
	else:
		if is_uuid4(mt):
			req = await Requestx.get(uuid=mt)
		else:
			msg = await message.answer('<b>❌ Не удалось найти запрос</b>', reply_markup=kb_back(f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}'))
			await state.update_data(msg=msg)
			return
	if not req:
		msg = await message.answer('<b>❌ Не удалось найти запрос</b>', reply_markup=kb_back(f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}'))
		await state.update_data(msg=msg)
		return
	await state.clear()

	files = [z for x in req.questions_answers.values() if isinstance(x, list) for z in x]
	text = message_tree_construct(req_type=req.req_type, req_sub_type=req.req_sub_type, answers=req.questions_answers, h1=False)
	await message.answer(f'<b>{"🔴" if req.completed else "🟢"} Информация о {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("p", "запросе")}</b>\n├ UUID {trns_all.get("morph", {}).get(req.req_type, {}).get("l", {}).get("r", "запроса")}:  <code>{req.uuid}</code>\n│\n{text}', reply_markup=kb_admin_request(tg_user_id, req, files, req_status, req_type, page, user_id))





@router.message(StateFilter('input_user_search'))
async def input_user_search(message: Message, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(message)
	mt = message.text.strip().replace('@', '')
	state_data = await state.get_data()
	await del_message(message, state_data.get('msg', None))
	if mt.isnumeric():
		mt = int(mt)
		if mt >= 2**31 - 1:
			user = await Userx.get(tg_user_id=mt, any_value=True)
		else:
			user = await Userx.get(id=mt, tg_user_id=mt, any_value=True)
	else:
		if is_uuid4(mt):
			request = await Requestx.get(uuid=mt)
			user = await Userx.get(id=request.user_id)
		else:
			user = await Userx.get(tg_username=mt)
	if not user:
		msg = await message.answer('<b>❌ Не удалось найти пользователя</b>', reply_markup=kb_admin_search())
		await state.update_data(msg=msg)
		return
	await state.clear()

	reg_date = datetime.fromtimestamp(user.created_at).strftime("%d.%m.%Y")
	if tg_user_id in moderator_ids:
		await message.answer(f'<b>Информация о пользователе</b>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(tg_user_id, user.id))
	else:
		await message.answer(f'<b>Информация о пользователе</b>\n├ Юзернейм: {user_format_url(user)}\n├ ID телеграма:  <code>{user.tg_user_id}</code>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(tg_user_id, user.id))

@router.message(StateFilter('user_dialogue'))
async def dialogue_handler(message: Message, bot: Bot, state: FSMContext):
	data = await state.get_data()
	user = data['user']
	admin = data['admin']
	dialogue = data['dialogue']

	if message.text and message.text != '':
		if message.text == '❌ Завершить диалог':
			del custom_fsm['dialogue'][user.tg_user_id]
			await state.clear()
			await message.answer('<b>Диалог с пользователем завершён</b>\n<i>Вы можете продолжить диалог в меню пользователя</i>', reply_markup=kb_back(f'admin:search:{user.id}'))
			await bot.send_message(user.tg_user_id, '<b>Диалог с администратором завершён</b>\n<i>Теперь администратор не будет получать ваши сообщения</i>', reply_markup=kb_close())
			return
		elif message.text == '📝 Сохранить диалог':
			await message.answer('Не реализовано', reply_markup=kb_close())
			return
	
	if message.content_type == 'text':
		text = message.html_text.replace(str(admin.tg_user_id), "").replace(f'@{admin.tg_username}', "").replace(str(admin.tg_username), "") if admin.tg_user_id in moderator_ids else message.html_text
		await bot.send_message(user.tg_user_id, text)
		message_id = message.message_id
	else:
		file_chat_id, file_message_id = await upload_file(bot, admin.tg_user_id, message.message_id)
		message_id = file_message_id
		await bot.copy_message(chat_id=user.tg_user_id, from_chat_id=file_chat_id, message_id=message_id)
	await DialogueMessagex.add(dialogue_id=dialogue.id, message_id=message_id, message_content_type=message.content_type, message_text=message.html_text, from_user_id=admin.id, from_user_tg_id=admin.tg_user_id, from_user_type='admin')