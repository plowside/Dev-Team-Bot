# -*- coding: utf- 8 -*-
import asyncio, random

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
		await call.message.edit_text('🧑🏻‍💻 Админ меню', reply_markup=kb_admin_menu())

	elif cd[1] == 'search':
		if len(cd) == 2:
			await state.set_state('input_user_search')
			msg = await call.message.edit_text('<b>👤 Поиск пользователя</b>\n<i>Введите user_id\\tg_id\\username пользователя</i>', reply_markup=kb_admin_search())
			await state.update_data(msg=msg)
		else:
			user_id = int(cd[2])
			user = await Userx.get(id=user_id)
			if not user:
				await call.answer('❌ Не удалось найти пользователя', show_alert=True)
				return

			reg_date = datetime.fromtimestamp(user.created_at).strftime("%d.%m.%Y")
			if tg_user_id in moderator_ids:
				await call.message.edit_text(f'<b>Информация о пользователе</b>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(user.id))
			else:
				await call.message.edit_text(f'<b>Информация о пользователе</b>\n├ user_id:  <code>{user.id}</code>\n├ tg_id:  <code>{user.tg_user_id}</code>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(user.id))
	
	elif cd[1] == 'dialogue':
		act = cd[2]
		user_id = int(cd[3])
		user = await Userx.get(id=user_id)
		admin = await Userx.get(tg_user_id=tg_user_id)

		if act == 'menu':
			dialogue = await Dialoguex.get(admin_user_id=admin.id, user_id=user.id, show=True)
			await call.message.edit_text('Меню диалога', reply_markup=kb_admin_user_dialogue(user.id, dialogue.id if dialogue else None))

		elif act == 'start':
			try: result = await bot.send_message(user.tg_user_id, f'Администратор начал с вами чат, все ваши сообщения будет получать администратор.')
			except: result = False
			if not result:
				await call.answer('🔐 Пользователь заблокировал бота', show_alert=True)
				return

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

			if not dialogue:
				return await call.answer('Не удалось получить историю диалога', show_alert=True)
			elif dialogue.admin_user_id != admin.id or dialogue.user_id != user.id:
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
					await bot.copy_message(chat_id=admin.tg_user_id, from_chat_id=message.from_user_tg_id, message_id=message.message_id, caption=prefix)

			custom_fsm['dialogue'][user.tg_user_id] = {'user': user, 'admin': admin, 'dialogue': dialogue, 'history': []}
			await state.set_state('user_dialogue')
			await state.update_data(user=user, admin=admin, dialogue=dialogue)
			await call.answer()
			await call.message.answer(f'Вы продолжили диалог с пользователем', reply_markup=kb_admin_dialogue())


	elif cd[1] == 'request':
		act = cd[2]
		req_id = int(cd[3])
		req_table = cd[4]
		req_status = int(cd[5]) if len(cd) >= 6 else 0
		req_type = int(cd[6]) if len(cd) >= 7 else 0
		page = int(cd[7]) if len(cd) >= 8 else 0
		user_id = int(cd[8]) if len(cd) >= 9 else None

		if act == 's':
			if req_table == 'designer':
				req = await Designerx.get(id=req_id)
			elif req_table == 'coder':
				req = await Coderx.get(id=req_id)
			elif req_table == 'order':
				req = await Orderx.get(id=req_id)
			trns = {
				'point_of_work': 'Суть заказа',
				'deadline': 'Дедлайн',
				'budget': 'Бюджет',
				'age': 'Возраст',
				'stack': 'Стек',
				'portfolio': 'Портфолио',
				'extra_information': 'Доп. информация',
				'complete_test_task': 'Готов к тестовому заданию',
				'services_provided': 'Предоставляемые услуги',
			}
			req_dict = {x[0]: x[1] for x in req.dict().items() if x[0] in trns}
			req_info_text = '\n'.join([f'{"├" if i != len(req_dict) else "└"} {trns[x]}:  <code>{("Да" if req_dict[x] else "Нет") if x == "complete_test_task" else req_dict[x]}</code>' for i, x in enumerate(req_dict, start=1)])
			await call.message.edit_text(f'<b>Информация о {"заказе" if req_table == "order" else "заявке"} {"🔴" if req.completed else "🟢"}</b>\n{req_info_text}', reply_markup=kb_admin_request(req_id, req_table, req.user_id, req_status, req_type, page, user_id))
		
		elif act == 'c':
			if req_table == 'designer':
				req = await Designerx.update(id=req_id, completed=True)
			elif req_table == 'coder':
				req = await Coderx.update(id=req_id, completed=True)
			elif req_table == 'order':
				req = await Orderx.update(id=req_id, completed=True)

			await call.answer(f'{"Заказ" if req_table == "order" else "Заявка"} отмечена как завершенн{"ый" if req_table == "order" else "ая"}', show_alert=True)
			await callback_admin(call, bot, state, f'admin:requests:{req_status}:{req_type}:{page}{":"+str(user_id) if user_id else ""}')


	elif cd[1] == 'requests':
		req_status = int(cd[2]) if len(cd) >= 3 else 0
		req_type = int(cd[3]) if len(cd) >= 4 else 0
		page = int(cd[4]) if len(cd) >= 5 else 0
		user_id = int(cd[5]) if len(cd) >= 6 else None

		sql_designers = "SELECT 'designer' AS q, id, user_id, NULL AS description, stack, NULL AS portfolio, services_provided AS extra_info1, extra_information AS extra_info2, created_at FROM designers" + (f' WHERE user_id = {user_id}' if user_id else '') + ((' AND completed = True' if user_id else ' WHERE completed = True') if req_status == 2 else (' AND completed = False' if user_id else ' WHERE completed = False') if req_status == 1 else '')
		sql_coders = "SELECT 'coder' AS q, id, user_id, NULL AS description, stack, portfolio, NULL AS extra_info1, extra_information AS extra_info2, created_at FROM coders" + (f' WHERE user_id = {user_id}' if user_id else '') + ((' AND completed = True' if user_id else ' WHERE completed = True') if req_status == 2 else (' AND completed = False' if user_id else ' WHERE completed = False') if req_status == 1 else '') + (' UNION ALL' if req_type == 0 else '')
		sql_orders = "SELECT 'order' AS q, id, user_id, point_of_work AS description, NULL AS stack, NULL AS portfolio, deadline AS extra_info1, budget AS extra_info2, created_at FROM orders" + (f' WHERE user_id = {user_id}' if user_id else '') + ((' AND completed = True' if user_id else ' WHERE completed = True') if req_status == 2 else (' AND completed = False' if user_id else ' WHERE completed = False') if req_status == 1 else '') + (' UNION ALL' if req_type == 0 else '')
		if req_type == 3: sql = sql_designers
		elif req_type == 2: sql = sql_coders
		elif req_type == 1: sql = sql_orders
		elif req_type == 0: sql = f'{sql_orders} {sql_coders} {sql_designers}'
		sql = f'{sql} ORDER BY created_at DESC'
		requests = await db.fetch(sql)
		items_for_page = paginate_list(requests, 6, page)

		await call.message.edit_text(f'Все запросы {"".join("⠀" for x in range(random.randint(1,9)))}', reply_markup=kb_admin_requests(items_for_page, req_status, req_type, (len(paginate_list(requests, 6, page - 1)) > 0, page, len(paginate_list(requests, 6, page + 1)) > 0), user_id))



@router.message(StateFilter('input_user_search'))
async def input_user_search(message: Message, bot: Bot, state: FSMContext):
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
		user = await Userx.get(tg_username=mt)
	if not user:
		msg = await message.answer('<b>❌ Не удалось найти пользователя</b>', reply_markup=kb_admin_search())
		await state.update_data(msg=msg)
		return

	reg_date = datetime.fromtimestamp(user.created_at).strftime("%d.%m.%Y")
	await message.answer(f'<b>Информация о пользователе</b>\n├ user_id:  <code>{user.id}</code>\n├ tg_id:  <code>{user.tg_user_id}</code>\n└ Дата регистрации:  <code>{reg_date}</code>', reply_markup=kb_admin_user(user.id))


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
		# custom_fsm['dialogue'][user.tg_user_id]['history'].append({'from': {'name': 'admin', 'tg_user_id': admin.tg_user_id}, 'text': message.text})
	
	if message.content_type == 'text':
		text = message.text.replace(str(admin.tg_user_id), "").replace(f'@{admin.tg_username}', "").replace(str(admin.tg_username), "") if admin.tg_user_id in moderator_ids else message.text
		await bot.send_message(user.tg_user_id, text)
	else:
		await bot.copy_message(chat_id=user.tg_user_id, from_chat_id=admin.tg_user_id, message_id=message.message_id)
	await DialogueMessagex.add(dialogue_id=dialogue.id, message_id=message.message_id, message_content_type=message.content_type, message_text=message.text, from_user_id=admin.id, from_user_tg_id=admin.tg_user_id, from_user_type='admin')